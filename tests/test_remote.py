"""Tests for the SFR Box Remote Home Assistant platform."""

from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PORT
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sfr_box_remote import async_setup_entry
from custom_components.sfr_box_remote import async_unload_entry
from custom_components.sfr_box_remote.const import DOMAIN
from custom_components.sfr_box_remote.remote import SFRBoxRemote
from sfr_tv_box_core.constants import CommandType
from sfr_tv_box_core.constants import KeyCode


@pytest.fixture
def config_entry(hass: HomeAssistant):
    """Create a mock SFR Box configuration entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.16",
            CONF_PORT: 7682,
            "device_id": "default-stb8",
        },
        unique_id="default-stb8",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_driver():
    """Create a simulated STB8 driver."""
    driver = MagicMock()
    driver.is_connected = True
    driver.start = AsyncMock()
    driver.stop = AsyncMock()
    driver.send_command = AsyncMock()
    return driver


@pytest.mark.asyncio
async def test_setup_entry_starts_driver_and_loads_remote(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
):
    """Test that setup starts the driver and loads the remote platform."""
    with (
        patch("custom_components.sfr_box_remote.STB8Driver") as driver_class,
        patch.object(
            hass.config_entries,
            "async_forward_entry_setups",
            new_callable=AsyncMock,
        ) as forward_platforms,
    ):
        driver = driver_class.return_value
        driver.start = AsyncMock()

        result = await async_setup_entry(hass, config_entry)

    assert result is True
    driver_class.assert_called_once_with(
        "192.168.1.16",
        7682,
        device_id="default-stb8",
    )
    driver.start.assert_awaited_once()
    forward_platforms.assert_awaited_once_with(
        config_entry,
        [Platform.REMOTE],
    )
    assert hass.data[DOMAIN][config_entry.entry_id] is driver


@pytest.mark.asyncio
async def test_unload_entry_stops_driver(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_driver,
):
    """Test that unloading the entry stops and removes the driver."""
    hass.data[DOMAIN] = {config_entry.entry_id: mock_driver}

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        new_callable=AsyncMock,
        return_value=True,
    ) as unload_platforms:
        result = await async_unload_entry(hass, config_entry)

    assert result is True
    unload_platforms.assert_awaited_once_with(
        config_entry,
        [Platform.REMOTE],
    )
    mock_driver.stop.assert_awaited_once()
    assert DOMAIN not in hass.data


@pytest.mark.asyncio
async def test_remote_platform_creates_entity(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_driver,
):
    """Test that the remote platform creates one entity."""
    from custom_components.sfr_box_remote.remote import async_setup_entry as setup_remote

    hass.data[DOMAIN] = {config_entry.entry_id: mock_driver}
    add_entities = MagicMock()

    await setup_remote(hass, config_entry, add_entities)

    add_entities.assert_called_once()
    entity = add_entities.call_args.args[0][0]
    assert isinstance(entity, SFRBoxRemote)
    assert entity.unique_id == config_entry.entry_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("command", "key"),
    [
        ("up", KeyCode.UP),
        ("down", KeyCode.DOWN),
        ("left", KeyCode.LEFT),
        ("right", KeyCode.RIGHT),
        ("ok", KeyCode.OK),
        ("back", KeyCode.BACK),
        ("home", KeyCode.HOME),
        ("volume_up", KeyCode.VOL_UP),
        ("volume_down", KeyCode.VOL_DOWN),
        ("mute", KeyCode.MUTE),
        ("channel_up", KeyCode.CHAN_UP),
        ("channel_down", KeyCode.CHAN_DOWN),
        ("play_pause", KeyCode.PLAY_PAUSE),
        ("fast_forward", KeyCode.FFWD),
        ("rewind", KeyCode.REWIND),
        ("stop", KeyCode.STOP),
        ("record", KeyCode.RECORD),
        ("power", KeyCode.POWER),
        ("0", KeyCode.NUM_0),
        ("1", KeyCode.NUM_1),
        ("2", KeyCode.NUM_2),
        ("3", KeyCode.NUM_3),
        ("4", KeyCode.NUM_4),
        ("5", KeyCode.NUM_5),
        ("6", KeyCode.NUM_6),
        ("7", KeyCode.NUM_7),
        ("8", KeyCode.NUM_8),
        ("9", KeyCode.NUM_9),
    ],
)
async def test_remote_command_mapping(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_driver,
    command: str,
    key: KeyCode,
):
    """Test that remote commands are translated into STB8 key codes."""
    entity = SFRBoxRemote(mock_driver, config_entry)

    await entity.async_send_command([command])

    mock_driver.send_command.assert_awaited_once_with(
        CommandType.SEND_KEY,
        key=key,
    )


@pytest.mark.asyncio
async def test_remote_availability(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_driver,
):
    """Test that availability follows the driver's connection state."""
    entity = SFRBoxRemote(mock_driver, config_entry)

    assert entity.available is True

    mock_driver.is_connected = False

    assert entity.available is False


@pytest.mark.asyncio
async def test_remote_does_not_send_command_when_disconnected(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_driver,
):
    """Test that commands are ignored when the decoder is disconnected."""
    mock_driver.is_connected = False
    entity = SFRBoxRemote(mock_driver, config_entry)

    await entity.async_send_command(["up"])

    mock_driver.send_command.assert_not_awaited()
