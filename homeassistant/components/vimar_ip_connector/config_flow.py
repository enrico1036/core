"""Config flow for Vimar IP Connector integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.config_entries import SOURCE_ZEROCONF

# from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_CODE,
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_IP_ADDRESS,
    CONF_MAC,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CODE): str,
        vol.Required(CONF_IP_ADDRESS): str,
        vol.Required(CONF_PORT): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    hub = PlaceholderHub(data["host"])

    if not await hub.authenticate(data["username"], data["password"]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Name of the device"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vimar IP Connector."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle setup by user for Modern Forms integration."""
        return await self._handle_config_flow(user_input)

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        host = discovery_info.hostname.rstrip(".")
        name, _ = host.rsplit(".")

        self.context.update(
            {
                CONF_IP_ADDRESS: discovery_info.hostname,
                CONF_PORT: discovery_info.port,
                CONF_DEVICE_ID: discovery_info.properties.get("deviceuid"),
                "title_placeholders": {"name": name},
            }
        )

        # Prepare configuration flow
        return await self._handle_config_flow({}, True)

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by zeroconf."""
        return await self._handle_config_flow(user_input)

    async def _handle_config_flow(
        self, user_input: dict[str, Any] | None = None, prepare: bool = False
    ) -> FlowResult:
        """Config flow handler for ModernForms."""
        source = self.context.get("source")

        # Request user input, unless we are preparing discovery flow
        if user_input is None:
            user_input = {}
            if not prepare:
                if source == SOURCE_ZEROCONF:
                    return self._show_confirm_dialog()
                return self._show_setup_form()

        if source == SOURCE_ZEROCONF:
            user_input[CONF_HOST] = self.context.get(CONF_HOST)
            user_input[CONF_PORT] = self.context.get(CONF_PORT)

        # if user_input.get(CONF_DEVICE_ID) is None or not prepare:
        #     session = async_get_clientsession(self.hass)
        #     device = ModernFormsDevice(user_input[CONF_HOST], session=session)
        #     try:
        #         device = await device.update()
        #     except ModernFormsConnectionError:
        #         if source == SOURCE_ZEROCONF:
        #             return self.async_abort(reason="cannot_connect")
        #         return self._show_setup_form({"base": "cannot_connect"})
        #     user_input[CONF_MAC] = device.info.mac_address
        #     user_input[CONF_NAME] = device.info.device_name

        # Check if already configured
        await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
        self._abort_if_unique_id_configured(
            updates={CONF_DEVICE_ID: user_input[CONF_DEVICE_ID]}
        )

        # title = device.info.device_name
        # if source == SOURCE_ZEROCONF:
        #     title = self.context.get(CONF_NAME)

        if prepare:
            return await self.async_step_zeroconf_confirm()

        return self.async_create_entry(
            title="title",
            data={CONF_HOST: user_input[CONF_HOST], CONF_MAC: user_input[CONF_MAC]},
        )

    def _show_setup_form(self, errors: dict | None = None) -> FlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors or {},
        )

    def _show_confirm_dialog(self, errors: dict | None = None) -> FlowResult:
        """Show the confirm dialog to the user."""
        name = self.context.get(CONF_DEVICE_ID)
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": name},
            errors=errors or {},
        )

    # async def async_step_zeroconf(
    #     self, discovery_info: DiscoveryInfoType
    # ) -> FlowResult:
    #     """Handle a flow initialized by discovery."""
    #     # Initialising empty dictionary
    #     data_str = {}

    #     # Converting
    #     for key, value in discovery_info["properties"].items():
    #         data_str[key.decode("utf-8")] = value.decode("utf-8")

    #     await self.async_set_unique_id(data_str["deviceuid"])
    #     self._abort_if_unique_id_configured(
    #         updates={
    #             "CONF_HOST": socket.inet_ntoa(discovery_info.addresses[0]),
    #             "CONF_PORT": discovery_info["port"],
    #         }
    #     )
    #     return self.async_step_user()

    # async def async_step_user(
    #     self, user_input: dict[str, Any] | None = None
    # ) -> FlowResult:
    #     """Handle the initial step."""
    #     if user_input is None:
    #         return self.async_show_form(
    #             step_id="user", data_schema=STEP_USER_DATA_SCHEMA
    #         )

    #     errors = {}

    #     try:
    #         info = await validate_input(self.hass, user_input)
    #     except CannotConnect:
    #         errors["base"] = "cannot_connect"
    #     except InvalidAuth:
    #         errors["base"] = "invalid_auth"
    #     except Exception:  # pylint: disable=broad-except
    #         _LOGGER.exception("Unexpected exception")
    #         errors["base"] = "unknown"
    #     else:
    #         return self.async_create_entry(title=info["title"], data=user_input)

    #     return self.async_show_form(
    #         step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
    #     )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
