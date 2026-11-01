"""Tests for the WebSocket reconnection lifecycle."""

import asyncio

import pytest
import websockets

from sfr_tv_box_core.base_driver import BaseSFRBoxDriver


class ConcreteDriver(BaseSFRBoxDriver):
    """Concrete driver used for reconnection tests."""

    async def _handle_message(self, message: str) -> None:
        pass


class BlockingWebSocket:
    """WebSocket that remains open until close() is called."""

    def __init__(self):
        """Initialize the simulated WebSocket."""
        self.closed = asyncio.Event()
        self.close_calls = 0

    def __aiter__(self):
        """Return the asynchronous iterator."""
        return self

    async def __anext__(self):
        """Wait until the WebSocket is closed."""
        await self.closed.wait()
        raise StopAsyncIteration

    async def close(self):
        """Close the simulated WebSocket."""
        self.close_calls += 1
        self.closed.set()


class ClosedWebSocket:
    """WebSocket whose message stream ends immediately."""

    def __aiter__(self):
        """Return the asynchronous iterator."""
        return self

    async def __anext__(self):
        """End the asynchronous message stream."""
        raise StopAsyncIteration

    async def close(self):
        """Close the simulated WebSocket."""
        pass


@pytest.fixture
def driver():
    """Provide a fresh driver."""
    return ConcreteDriver(host="localhost", port=1234)


@pytest.mark.asyncio
async def test_start_is_non_blocking_and_idempotent(driver, monkeypatch):
    """start() must return promptly and create only one connection task."""
    connect_started = asyncio.Event()
    calls = []

    async def blocked_connect(uri):
        calls.append(uri)
        connect_started.set()
        await asyncio.Future()

    monkeypatch.setattr(websockets, "connect", blocked_connect)

    await asyncio.wait_for(driver.start(), timeout=1)
    await asyncio.wait_for(connect_started.wait(), timeout=1)

    task = driver._reconnect_task
    await driver.start()

    assert driver._reconnect_task is task
    assert len(calls) == 1

    await driver.stop()
    assert task.done()


@pytest.mark.asyncio
async def test_reconnects_after_initial_connection_failure(driver, monkeypatch):
    """A failed connection must be retried with exponential backoff."""
    original_sleep = asyncio.sleep
    delays = []
    connected = asyncio.Event()
    attempts = 0
    websocket = BlockingWebSocket()

    async def fast_sleep(delay):
        delays.append(delay)
        await original_sleep(0)

    async def fake_connect(uri):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("Connection refused")
        connected.set()
        return websocket

    monkeypatch.setattr(
        "sfr_tv_box_core.base_driver.asyncio.sleep",
        fast_sleep,
    )
    monkeypatch.setattr(websockets, "connect", fake_connect)

    await driver.start()
    await asyncio.wait_for(connected.wait(), timeout=2)

    assert attempts >= 2
    assert delays[0] == 1

    await driver.stop()


@pytest.mark.asyncio
async def test_reconnects_after_unexpected_disconnect(driver, monkeypatch):
    """An ended message stream must trigger a new connection."""
    original_sleep = asyncio.sleep
    attempts = 0
    second_connection = asyncio.Event()
    websocket = BlockingWebSocket()

    async def fast_sleep(delay):
        await original_sleep(0)

    async def fake_connect(uri):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return ClosedWebSocket()
        second_connection.set()
        return websocket

    monkeypatch.setattr(
        "sfr_tv_box_core.base_driver.asyncio.sleep",
        fast_sleep,
    )
    monkeypatch.setattr(websockets, "connect", fake_connect)

    await driver.start()
    await asyncio.wait_for(second_connection.wait(), timeout=2)

    assert attempts >= 2

    await driver.stop()


@pytest.mark.asyncio
async def test_stop_during_connection_attempt(driver, monkeypatch):
    """stop() must cancel an in-progress connection attempt."""
    connect_started = asyncio.Event()

    async def blocked_connect(uri):
        connect_started.set()
        await asyncio.Future()

    monkeypatch.setattr(websockets, "connect", blocked_connect)

    await driver.start()
    await asyncio.wait_for(connect_started.wait(), timeout=1)

    task = driver._reconnect_task
    await driver.stop()

    assert task.done()
    assert driver._reconnect_task is None


@pytest.mark.asyncio
async def test_stop_during_listening_and_repeated_stop(driver, monkeypatch):
    """stop() must close the socket and safely tolerate repeated calls."""
    connected = asyncio.Event()
    websocket = BlockingWebSocket()

    async def fake_connect(uri):
        connected.set()
        return websocket

    monkeypatch.setattr(websockets, "connect", fake_connect)

    await driver.start()
    await asyncio.wait_for(connected.wait(), timeout=1)

    task = driver._reconnect_task

    await driver.stop()
    await driver.stop()

    assert task.done()
    assert websocket.closed.is_set()
    assert websocket.close_calls >= 1
    assert driver._websocket is None
    assert driver._reconnect_task is None


@pytest.mark.asyncio
async def test_is_connected_tracks_websocket_lifecycle(driver, monkeypatch):
    """is_connected must reflect the WebSocket connection lifecycle."""
    connected = asyncio.Event()
    websocket = BlockingWebSocket()

    async def fake_connect(uri):
        connected.set()
        return websocket

    monkeypatch.setattr(websockets, "connect", fake_connect)

    assert driver.is_connected is False

    await driver.start()
    await asyncio.wait_for(connected.wait(), timeout=1)

    assert driver.is_connected is True

    await driver.stop()

    assert driver.is_connected is False
