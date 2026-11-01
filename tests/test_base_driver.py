"""Tests for the `BaseSFRBoxDriver` abstract base class."""

import asyncio
import logging
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import call

import pytest
import websockets

from sfr_tv_box_core.base_driver import BaseSFRBoxDriver
from sfr_tv_box_core.constants import DEFAULT_WEBSOCKET_PORT


# Since we are testing the abstract base class, we need a concrete implementation.
class ConcreteDriver(BaseSFRBoxDriver):
    """A concrete implementation of `BaseSFRBoxDriver` for testing purposes."""

    def __init__(self, *args, **kwargs):
        """Initializes the `ConcreteDriver` and a list to store handled messages."""
        super().__init__(*args, **kwargs)
        self.handled_messages = []

    async def _handle_message(self, message: str):
        """Handles a message by appending it to the `handled_messages` list."""
        self.handled_messages.append(message)


@pytest.fixture
def driver():
    """Provides a fresh instance of the ConcreteDriver for each test."""
    return ConcreteDriver(host="localhost", port=1234)


@pytest.mark.asyncio
async def test_driver_initialization(driver):
    """Test that the driver initializes correctly."""
    assert driver._host == "localhost"
    assert driver._port == 1234
    assert driver._websocket is None


@pytest.mark.asyncio
async def test_connect_success(driver, monkeypatch):
    """Test a successful connection using monkeypatch."""
    mock_ws = AsyncMock()
    # Create an async mock for the connect function
    mock_connect = AsyncMock(return_value=mock_ws)
    # Use monkeypatch to replace websockets.connect with our mock
    monkeypatch.setattr(websockets, "connect", mock_connect)

    await driver._connect()

    mock_connect.assert_called_once_with("ws://localhost:1234/ws")
    assert driver._websocket is mock_ws


@pytest.mark.asyncio
async def test_connect_with_retries(driver, monkeypatch):
    """Test connection with retries on failure using monkeypatch."""
    # Create an async mock that will simulate failures then success
    mock_connect = AsyncMock(
        side_effect=[
            websockets.exceptions.ConnectionClosedError(None, None),
            Exception("Some other connection error"),
            AsyncMock(),  # Successful connection on the third try
        ]
    )
    monkeypatch.setattr(websockets, "connect", mock_connect)
    # Patch asyncio.sleep to capture calls and prevent actual delays
    sleep_mock = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep_mock)

    await driver._connect()

    assert mock_connect.call_count == 3
    assert sleep_mock.call_count == 2
    assert driver._websocket is not None

    # Assert that the sleep delays were exponential (1s, then 2s)
    sleep_mock.assert_has_calls(
        [
            call(1),  # First retry after 1 second
            call(2),  # Second retry after 2 seconds
        ]
    )


@pytest.mark.asyncio
async def test_send_message_when_connected(driver):
    """Test sending a message when the WebSocket is connected."""
    driver._websocket = AsyncMock()
    await driver.send_message("test message")
    driver._websocket.send.assert_called_once_with("test message")


@pytest.mark.asyncio
async def test_listen_for_messages_and_handle(driver):
    """Test that the message listener loop correctly handles incoming messages."""
    mock_ws = AsyncMock()
    # To mock the async iterator `async for message in self._websocket:`
    mock_ws.__aiter__.return_value = ["msg1", "msg2"]
    driver._websocket = mock_ws

    listener_mock = MagicMock()
    driver.register_listener(listener_mock)

    await driver._listen_for_messages()

    # Check that the internal handler was called
    assert driver.handled_messages == ["msg1", "msg2"]
    # Check that the external listener was called
    listener_mock.assert_any_call("msg1")
    listener_mock.assert_any_call("msg2")
    assert listener_mock.call_count == 2


@pytest.mark.asyncio
async def test_listener_registration(driver):
    """Test registering and unregistering message listeners."""
    listener1 = MagicMock()
    listener2 = MagicMock()

    driver.register_listener(listener1)
    assert listener1 in driver._listeners

    driver.register_listener(listener2)
    assert listener2 in driver._listeners

    driver.unregister_listener(listener1)
    assert listener1 not in driver._listeners
    assert listener2 in driver._listeners


@pytest.mark.asyncio
async def test_set_message_callback(driver):
    """Test that `set_message_callback` clears old listeners and sets one."""
    listener1 = MagicMock()
    listener2 = MagicMock()
    new_callback = MagicMock()

    driver.register_listener(listener1)
    driver.register_listener(listener2)
    assert len(driver._listeners) == 2

    driver.set_message_callback(new_callback)
    assert len(driver._listeners) == 1
    assert new_callback in driver._listeners
    assert listener1 not in driver._listeners
    assert listener2 not in driver._listeners


@pytest.mark.asyncio
async def test_send_message_when_not_connected(driver, caplog):
    """Test that `send_message` logs a warning when not connected."""
    assert driver._websocket is None  # Ensure we start disconnected
    await driver.send_message("this should not be sent")
    assert "Cannot send message: WebSocket not connected." in caplog.text


@pytest.mark.asyncio
async def test_stop_on_stopped_driver(driver):
    """Test that `stop` can be called on an already stopped driver without error."""
    # Ensure driver is in a "stopped" state
    assert driver._websocket is None
    assert driver._reconnect_task is None

    # Calling stop should do nothing and not raise an exception
    await driver.stop()
    await driver.stop()  # Call it again to be sure


@pytest.mark.asyncio
async def test_listen_for_messages_returns_on_connection_closed(driver, monkeypatch, caplog):
    """A connection closure must not recursively restart the driver."""
    caplog.set_level(logging.INFO)
    driver.start = AsyncMock()
    driver.stop = AsyncMock()

    mock_ws = AsyncMock()
    mock_ws.__aiter__.side_effect = websockets.exceptions.ConnectionClosed(None, None)
    driver._websocket = mock_ws

    await driver._listen_for_messages()

    driver.stop.assert_not_awaited()
    driver.start.assert_not_awaited()


@pytest.mark.asyncio
async def test_listen_for_messages_returns_on_exception(driver, monkeypatch, caplog):
    """A listening exception must not recursively restart the driver."""
    caplog.set_level(logging.ERROR)
    driver.start = AsyncMock()
    driver.stop = AsyncMock()

    mock_ws = AsyncMock()
    mock_ws.__aiter__.side_effect = Exception("Simulated listening error")
    driver._websocket = mock_ws

    await driver._listen_for_messages()

    driver.stop.assert_not_awaited()
    driver.start.assert_not_awaited()
    assert "Error during message listening: Simulated listening error" in caplog.text


@pytest.mark.asyncio
async def test_driver_initialization_default_port():
    """Test that the driver uses the default port if none is provided."""
    driver = ConcreteDriver(host="localhost")
    assert driver._port == DEFAULT_WEBSOCKET_PORT


@pytest.mark.asyncio
async def test_start_creates_supervisor_task(monkeypatch):
    """start() must return without waiting for the WebSocket connection."""
    driver = ConcreteDriver(host="localhost", port=1234)
    connected = asyncio.Event()
    listening = asyncio.Event()
    mock_ws = AsyncMock()

    async def fake_connect(uri):
        connected.set()
        return mock_ws

    async def blocked_listen():
        listening.set()
        await asyncio.Future()

    monkeypatch.setattr(websockets, "connect", fake_connect)
    listen_mock = AsyncMock(side_effect=blocked_listen)
    monkeypatch.setattr(driver, "_listen_for_messages", listen_mock)

    await asyncio.wait_for(driver.start(), timeout=1)
    await asyncio.wait_for(connected.wait(), timeout=1)
    await asyncio.wait_for(listening.wait(), timeout=1)

    assert driver._reconnect_task is not None
    assert not driver._reconnect_task.done()
    listen_mock.assert_awaited_once()

    await driver.stop()


@pytest.mark.asyncio
async def test_stop_cancels_task_and_closes_websocket():
    """stop() must close the socket and cancel and await the supervisor."""
    driver = ConcreteDriver(host="localhost", port=1234)
    mock_ws = AsyncMock()

    async def wait_forever():
        await asyncio.Future()

    task = asyncio.create_task(wait_forever())
    driver._websocket = mock_ws
    driver._reconnect_task = task

    await driver.stop()

    mock_ws.close.assert_awaited_once()
    assert task.done()
    assert task.cancelled()
    assert driver._websocket is None
    assert driver._reconnect_task is None


@pytest.mark.asyncio
async def test_listen_loop_returns_on_handler_exception(monkeypatch, caplog):
    """A handler exception must not recursively restart the driver."""
    driver = ConcreteDriver(host="localhost", port=1234)
    caplog.set_level(logging.ERROR)

    start_mock = AsyncMock()
    stop_mock = AsyncMock()
    monkeypatch.setattr(driver, "start", start_mock)
    monkeypatch.setattr(driver, "stop", stop_mock)

    mock_ws = AsyncMock()
    mock_ws.__aiter__.return_value = ["a message"]
    driver._websocket = mock_ws

    error_message = "Handler failed!"

    async def raise_exception(*args, **kwargs):
        raise Exception(error_message)

    handle_mock = AsyncMock(side_effect=raise_exception)
    monkeypatch.setattr(driver, "_handle_message", handle_mock)

    await driver._listen_for_messages()

    handle_mock.assert_awaited_once_with("a message")
    assert error_message in caplog.text
    stop_mock.assert_not_awaited()
    start_mock.assert_not_awaited()
