"""Local OCPP 1.6J central system for Easee chargers, hosted inside Home Assistant."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_ALLOWED_ID_TAGS,
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
    """Add the OCPP entities of every charger, each assigned to its subentry."""
    hub = get_ocpp_hub(hass)
    if hub is None:
        return
    for serial in hub.serials():
        async_add_entities(
            entities_for_charger(hub, serial),
            config_subentry_id=hub.config(serial).subentry_id,
        )


def get_ocpp_hub(hass: HomeAssistant) -> OcppHub | None:
    """Return the hub of the loaded config entry."""
    hub: OcppHub | None = hass.data.get(HUB_DATA_KEY)
    return hub
