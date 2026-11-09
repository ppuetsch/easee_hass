"""Local OCPP 1.6J central system for Easee chargers, hosted inside Home Assistant."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_ALLOWED_ID_TAGS,
    OCPP_UNIQUE_ID_MARKER,
    CONF_OCPP_PASSWORD,
    CONF_SERIAL,
    SUBENTRY_TYPE_OCPP_CHARGER,
)
from .hub import IdTagWhitelist, OcppChargerConfig, OcppHub
from .models import Serial
from .server import HUB_DATA_KEY, OcppWebSocketView


def async_register_ocpp_view(hass: HomeAssistant) -> None:
    """Register the websocket endpoint once; it finds the current hub at request time."""
    hass.http.register_view(OcppWebSocketView())


def ocpp_charger_configs(entry: ConfigEntry) -> list[OcppChargerConfig]:
    """Return the chargers that have an OCPP subentry."""
    return [
        OcppChargerConfig(
            serial=subentry.data[CONF_SERIAL],
            password=subentry.data[CONF_OCPP_PASSWORD],
            subentry_id=subentry.subentry_id,
        )
        for subentry in entry.subentries.values()
        if subentry.subentry_type == SUBENTRY_TYPE_OCPP_CHARGER
    ]


async def async_setup_ocpp_hub(hass: HomeAssistant, entry: ConfigEntry) -> OcppHub:
    """Create the hub for the chargers of this config entry."""
    whitelist = IdTagWhitelist(entry.options.get(CONF_ALLOWED_ID_TAGS, []))
    hub = OcppHub(hass, ocpp_charger_configs(entry), whitelist)
    await hub.async_load()
    remove_entities_of_removed_chargers(hass, entry, set(hub.serials()))
    hass.data[HUB_DATA_KEY] = hub
    return hub


async def async_unload_ocpp_hub(hass: HomeAssistant) -> None:
    """Close all OCPP connections."""
    hub: OcppHub | None = hass.data.pop(HUB_DATA_KEY, None)
    if hub is not None:
        await hub.async_shutdown()


def async_add_ocpp_entities(
    hass: HomeAssistant,
    async_add_entities: AddConfigEntryEntitiesCallback,
    entities_for_charger: Callable[[OcppHub, Serial], Iterable[Entity]],
) -> None:
    """Add the OCPP entities of every charger.

    They deliberately belong to no subentry: since HA 2026.11 a device belongs to exactly
    one subentry, and the cloud entities of the same charger device belong to none.
    Mixing both moves the device back and forth and HA deletes the other side's entities.
    """
    hub = get_ocpp_hub(hass)
    if hub is None:
        return
    for serial in hub.serials():
        async_add_entities(entities_for_charger(hub, serial))


def is_ocpp_unique_id_of_other_charger(unique_id: str, configured_serials: set[Serial]) -> bool:
    """Return True for an OCPP entity whose charger no longer has a subentry."""
    serial, separator, _ = unique_id.partition(OCPP_UNIQUE_ID_MARKER)
    return bool(separator) and serial not in configured_serials


def remove_entities_of_removed_chargers(
    hass: HomeAssistant, entry: ConfigEntry, configured_serials: set[Serial]
) -> None:
    """Delete OCPP entities of chargers whose subentry was removed (HA can't do it, see above)."""
    registry = er.async_get(hass)
    for registry_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if is_ocpp_unique_id_of_other_charger(registry_entry.unique_id, configured_serials):
            registry.async_remove(registry_entry.entity_id)


def get_ocpp_hub(hass: HomeAssistant) -> OcppHub | None:
    """Return the hub of the loaded config entry."""
    hub: OcppHub | None = hass.data.get(HUB_DATA_KEY)
    return hub
