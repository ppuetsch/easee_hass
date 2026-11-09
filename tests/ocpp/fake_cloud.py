"""Stand-in for the Easee cloud controller, so the integration loads without network access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from custom_components.easee.const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr


@dataclass(frozen=True)
class FakeCloudCharger:
    """The few charger attributes the OCPP code reads from the cloud side."""

    id: str
    name: str


class FakeController:
    """Creates the charger devices like the cloud entities would, but no cloud entities."""

    chargers: list[FakeCloudCharger] = []

    def __init__(self, username: str, password: str, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Mirror the real constructor."""
        self.hass = hass
        self.entry = config_entry

    async def async_initialize(self) -> None:
        """Register one device per charger."""
        registry = dr.async_get(self.hass)
        for charger in self.chargers:
            registry.async_get_or_create(
                config_entry_id=self.entry.entry_id,
                identifiers={(DOMAIN, charger.id)},
                name=charger.name,
                manufacturer="Easee",
            )

    async def async_cleanup(self) -> None:
        """Mirror the real cleanup."""
        self.hass.data[DOMAIN].pop("controller")

    async def async_setup_done(self, name: str) -> None:
        """Nothing to track."""

    def get_chargers(self) -> list[FakeCloudCharger]:
        """Chargers of the account."""
        return self.chargers

    def get_equalizers(self) -> list[Any]:
        """No equalizers."""
        return []

    def get_sites(self) -> list[dict[str, str]]:
        """One site."""
        return [{"name": "Home"}]

    def _no_entities(self) -> list[Any]:
        return []

    get_binary_sensor_entities = _no_entities
    get_button_entities = _no_entities
    get_light_entities = _no_entities
    get_sensor_entities = _no_entities
    get_switch_entities = _no_entities
