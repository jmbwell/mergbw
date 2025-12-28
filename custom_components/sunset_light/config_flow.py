"""Config flow for Sunset Light."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_MAC

from .const import CONF_PROFILE, DEFAULT_PROFILE, DOMAIN
from .protocol import list_profiles

_LOGGER = logging.getLogger(__name__)

class SunsetLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sunset Light."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_MAC])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Sunset Light", data=user_input)

        profile_options = {key: label for key, label in list_profiles()}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_MAC): str,
                vol.Required(CONF_PROFILE, default=DEFAULT_PROFILE): vol.In(profile_options),
            }),
            errors=errors,
        )
