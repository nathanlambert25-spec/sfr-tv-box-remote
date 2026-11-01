"""SFR Box Remote integration."""

from homeassistant.const import Platform

from sfr_tv_box_core.stb8_driver import STB8Driver

from .const import DOMAIN

PLATFORMS = [Platform.REMOTE]


async def async_setup_entry(hass, entry):
    """Set up the SFR Box Remote integration."""
    driver = STB8Driver(
        entry.data["host"],
        entry.data["port"],
        device_id=entry.data["device_id"],
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = driver

    await driver.start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    """Unload the SFR Box Remote integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        driver = hass.data[DOMAIN].pop(entry.entry_id)
        await driver.stop()

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok
