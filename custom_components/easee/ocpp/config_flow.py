"""Config subentry flow: connect one Easee charger to Home Assistant via OCPP."""

from __future__ import annotations

import secrets
import string
from typing import Any

import probatio

from homeassistant.config_entries import ConfigSubentryFlow, SubentryFlowResult
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

from ..const import DOMAIN
from .const import CONF_OCPP_PASSWORD, CONF_SERIAL, OCPP_PASSWORD_LENGTH

type ChargerChoices = dict[str, str]

PASSWORD_ALPHABET = string.ascii_letters + string.digits


def generate_ocpp_password() -> str:
    """Random basic auth password within the Easee length limit."""
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(OCPP_PASSWORD_LENGTH))


class OcppChargerSubentryFlow(ConfigSubentryFlow):
    """Adds one charger as OCPP charge point."""

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        """Let the user pick a charger that is not connected via OCPP yet."""
        choices = self._unconfigured_chargers()
        if not choices:
            return self.async_abort(reason="no_unconfigured_chargers")
        if user_input is not None:
            serial = user_input[CONF_SERIAL]
            return self.async_create_entry(
                title=f"OCPP {choices[serial]}",
                data={CONF_SERIAL: serial, CONF_OCPP_PASSWORD: generate_ocpp_password()},
                unique_id=serial,
            )
        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema(
                {probatio.Required(CONF_SERIAL): charger_selector(choices)}
            ),
        )

    def _unconfigured_chargers(self) -> ChargerChoices:
        configured = {
            subentry.unique_id for subentry in self._get_entry().subentries.values()
        }
        controller = self.hass.data[DOMAIN]["controller"]
        return {
            charger.id: f"{charger.name} ({charger.id})"
            for charger in controller.get_chargers()
            if charger.id not in configured
        }


def charger_selector(choices: ChargerChoices) -> SelectSelector:
    """Dropdown of chargers, showing name and serial."""
    options = [SelectOptionDict(value=serial, label=label) for serial, label in choices.items()]
    return SelectSelector(SelectSelectorConfig(options=options))
