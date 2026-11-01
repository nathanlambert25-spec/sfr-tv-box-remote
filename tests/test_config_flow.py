"""Tests for the SFR Box Remote Home Assistant config flow."""

from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sfr_box_remote.const import DOMAIN


@pytest.fixture(autouse=True)
def enable_custom_integrations_fixture(enable_custom_integrations):
    """Enable custom integrations for tests."""


@pytest.fixture
def valid_input():
    """Return valid configuration data."""
    return {
        CONF_HOST: "192.168.1.16",
        CONF_PORT: 7682,
        "device_id": "default-stb8",
    }


async def start_user_flow(hass: HomeAssistant):
    """Start the user configuration flow."""
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )


@pytest.mark.asyncio
async def test_form_is_shown(hass: HomeAssistant):
    """Test that the user configuration form is displayed."""
    result = await start_user_flow(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_successful_connection(
    hass: HomeAssistant,
    valid_input: dict,
):
    """Test that a successful WebSocket connection creates an entry."""
    mock_websocket = AsyncMock()

    with patch(
        "custom_components.sfr_box_remote.config_flow.websockets.connect",
        new_callable=AsyncMock,
        return_value=mock_websocket,
    ) as mock_connect:
        flow = await start_user_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            user_input=valid_input,
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "SFR Box Remote"
    assert result["data"] == valid_input
    mock_connect.assert_awaited_once_with("ws://192.168.1.16:7682/ws")
    mock_websocket.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_connection_failure(
    hass: HomeAssistant,
    valid_input: dict,
):
    """Test that an unreachable decoder returns cannot_connect."""
    with patch(
        "custom_components.sfr_box_remote.config_flow.websockets.connect",
        new_callable=AsyncMock,
        side_effect=OSError,
    ):
        flow = await start_user_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            user_input=valid_input,
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_invalid_host(
    hass: HomeAssistant,
    valid_input: dict,
):
    """Test that an invalid IP address is rejected."""
    valid_input[CONF_HOST] = "not-an-ip"

    flow = await start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=valid_input,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_host"}


@pytest.mark.asyncio
async def test_invalid_port(
    hass: HomeAssistant,
    valid_input: dict,
):
    """Test that an invalid WebSocket port is rejected."""
    valid_input[CONF_PORT] = 70000

    flow = await start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=valid_input,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_port"}


@pytest.mark.asyncio
async def test_already_configured(
    hass: HomeAssistant,
    valid_input: dict,
):
    """Test that a decoder ID cannot be configured twice."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=valid_input,
        unique_id="default-stb8",
    )
    entry.add_to_hass(hass)

    flow = await start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=valid_input,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "already_configured"}
