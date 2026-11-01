"""Remote platform for the SFR Box Remote integration."""

from collections.abc import Iterable

from homeassistant.components.remote import RemoteEntity

from sfr_tv_box_core.constants import CommandType
from sfr_tv_box_core.constants import KeyCode

from .const import DOMAIN

COMMAND_MAP = {
    "up": KeyCode.UP,
    "down": KeyCode.DOWN,
    "left": KeyCode.LEFT,
    "right": KeyCode.RIGHT,
    "ok": KeyCode.OK,
    "back": KeyCode.BACK,
    "home": KeyCode.HOME,
    "volume_up": KeyCode.VOL_UP,
    "volume_down": KeyCode.VOL_DOWN,
    "mute": KeyCode.MUTE,
    "channel_up": KeyCode.CHAN_UP,
    "channel_down": KeyCode.CHAN_DOWN,
    "play_pause": KeyCode.PLAY_PAUSE,
    "fast_forward": KeyCode.FFWD,
    "rewind": KeyCode.REWIND,
    "stop": KeyCode.STOP,
    "record": KeyCode.RECORD,
    "power": KeyCode.POWER,
    **{
        str(number): key
        for number, key in enumerate(
            (
                KeyCode.NUM_0,
                KeyCode.NUM_1,
                KeyCode.NUM_2,
                KeyCode.NUM_3,
                KeyCode.NUM_4,
                KeyCode.NUM_5,
                KeyCode.NUM_6,
                KeyCode.NUM_7,
                KeyCode.NUM_8,
                KeyCode.NUM_9,
            )
        )
    },
}


class SFRBoxRemote(RemoteEntity):
    """Representation of the SFR TV box remote."""

    _attr_name = "SFR Box Remote"

    def __init__(self, driver, config_entry):
        """Initialize the remote entity."""
        self._driver = driver
        self._attr_unique_id = config_entry.entry_id

    @property
    def available(self) -> bool:
        """Return whether the decoder is connected."""
        return self._driver.is_connected

    async def async_send_command(
        self,
        command: Iterable[str],
        **kwargs,
    ) -> None:
        """Send commands to the decoder."""
        if not self.available:
            return

        for name in command:
            key = COMMAND_MAP.get(name)
            if key is not None:
                await self._driver.send_command(
                    CommandType.SEND_KEY,
                    key=key,
                )


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the SFR Box Remote platform."""
    driver = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SFRBoxRemote(driver, entry)])
