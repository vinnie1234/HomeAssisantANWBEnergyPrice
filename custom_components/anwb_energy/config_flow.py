import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_ELECTRICITY, CONF_GAS


class ANWBEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            if not user_input.get(CONF_ELECTRICITY) and not user_input.get(CONF_GAS):
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._schema(),
                    errors={"base": "at_least_one"},
                )
            return self.async_create_entry(title="ANWB Energy", data=user_input)

        return self.async_show_form(step_id="user", data_schema=self._schema())

    @staticmethod
    def _schema() -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_ELECTRICITY, default=True): bool,
                vol.Required(CONF_GAS, default=True): bool,
            }
        )
