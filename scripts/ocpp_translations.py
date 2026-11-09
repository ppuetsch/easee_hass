"""Single source of the English and German texts of the local OCPP feature.

Merges them into strings.json, translations/en.json and translations/de.json, so the
three files never drift apart. Run after changing a text:

    python scripts/ocpp_translations.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

type Texts = dict[str, Any]

INTEGRATION_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "easee"

STATUS_STATES_EN = {
    "available": "Available", "preparing": "Preparing", "charging": "Charging",
    "suspendedevse": "Suspended by charger", "suspendedev": "Suspended by vehicle",
    "finishing": "Finishing", "reserved": "Reserved", "unavailable": "Unavailable", "faulted": "Faulted",
}
STATUS_STATES_DE = {
    "available": "Verfügbar", "preparing": "Vorbereitung", "charging": "Lädt",
    "suspendedevse": "Pausiert durch Charger", "suspendedev": "Pausiert durch Fahrzeug",
    "finishing": "Beendet", "reserved": "Reserviert", "unavailable": "Nicht verfügbar", "faulted": "Fehler",
}


def entity_names(names: dict[str, dict[str, str]]) -> dict[str, dict[str, Any]]:
    """Turn {platform: {key: name}} into the translation structure with ocpp_ prefix."""
    return {
        platform: {f"ocpp_{key}": {"name": name} for key, name in keys.items()}
        for platform, keys in names.items()
    }


ENTITY_NAMES_EN = {
    "sensor": {
        "status": "OCPP status", "power": "OCPP power", "energy": "OCPP energy meter",
        "session_energy": "OCPP session energy", "session_start": "OCPP session start",
        "current_offered": "OCPP current offered", "charging_limit": "OCPP charging limit",
        "temperature": "OCPP temperature",
        "current_l1": "OCPP current L1", "current_l2": "OCPP current L2", "current_l3": "OCPP current L3",
        "voltage_l1": "OCPP voltage L1", "voltage_l2": "OCPP voltage L2", "voltage_l3": "OCPP voltage L3",
        "last_rfid_card": "OCPP last RFID card", "error_code": "OCPP error code",
        "vendor_error_code": "OCPP vendor error code", "transaction_id": "OCPP transaction id",
        "last_message": "OCPP last message", "meter_value_interval": "OCPP meter value interval",
        "firmware": "OCPP firmware",
    },
    "binary_sensor": {
        "connected": "OCPP connected", "transaction": "OCPP session active", "charging": "OCPP charging",
    },
}
ENTITY_NAMES_DE = {
    "sensor": {
        "status": "OCPP-Status", "power": "OCPP-Leistung", "energy": "OCPP-Zählerstand",
        "session_energy": "OCPP-Energie Ladevorgang", "session_start": "OCPP-Beginn Ladevorgang",
        "current_offered": "OCPP-angebotener Strom", "charging_limit": "OCPP-Ladelimit",
        "temperature": "OCPP-Temperatur",
        "current_l1": "OCPP-Strom L1", "current_l2": "OCPP-Strom L2", "current_l3": "OCPP-Strom L3",
        "voltage_l1": "OCPP-Spannung L1", "voltage_l2": "OCPP-Spannung L2", "voltage_l3": "OCPP-Spannung L3",
        "last_rfid_card": "OCPP-letzte RFID-Karte", "error_code": "OCPP-Fehlercode",
        "vendor_error_code": "OCPP-Herstellerfehlercode", "transaction_id": "OCPP-Transaktions-ID",
        "last_message": "OCPP-letzte Nachricht", "meter_value_interval": "OCPP-Messintervall",
        "firmware": "OCPP-Firmware",
    },
    "binary_sensor": {
        "connected": "OCPP verbunden", "transaction": "OCPP-Ladevorgang aktiv", "charging": "OCPP lädt",
    },
}

SUBENTRY_EN: Texts = {
    "entry_type": "OCPP charger",
    "initiate_flow": {"user": "Connect charger via local OCPP"},
    "step": {
        "user": {
            "title": "Connect charger via local OCPP",
            "description": "Select the charger that should connect directly to Home Assistant.",
            "data": {"serial": "Charger"},
        }
    },
    "abort": {"no_unconfigured_chargers": "All chargers are already connected via OCPP."},
}
SUBENTRY_DE: Texts = {
    "entry_type": "OCPP-Charger",
    "initiate_flow": {"user": "Charger per lokalem OCPP verbinden"},
    "step": {
        "user": {
            "title": "Charger per lokalem OCPP verbinden",
            "description": "Wähle den Charger, der sich direkt mit Home Assistant verbinden soll.",
            "data": {"serial": "Charger"},
        }
    },
    "abort": {"no_unconfigured_chargers": "Alle Charger sind bereits per OCPP verbunden."},
}

OPTIONS_EN = {"allowed_id_tags": "RFID cards allowed to charge (OCPP)"}
OPTIONS_DE = {"allowed_id_tags": "RFID-Karten mit Ladefreigabe (OCPP)"}


def language_texts(entity_names_by_platform: dict[str, dict[str, str]], status_states: dict[str, str],
                   subentry: Texts, options: dict[str, str]) -> Texts:
    """Bundle all OCPP texts of one language."""
    entities = entity_names(entity_names_by_platform)
    entities["sensor"]["ocpp_status"]["state"] = status_states
    return {"entity": entities, "subentry": subentry, "options": options}


def deep_merge(target: Texts, addition: Texts) -> None:
    """Merge addition into target, replacing leaves."""
    for key, value in addition.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = value


def merge_into(path: Path, texts: Texts) -> None:
    """Write the OCPP texts into one translation file."""
    document = json.loads(path.read_text(encoding="utf-8"))
    deep_merge(document.setdefault("entity", {}), texts["entity"])
    document.setdefault("config_subentries", {})["ocpp_charger"] = texts["subentry"]
    options_data = document.setdefault("options", {}).setdefault("step", {}).setdefault("init", {}).setdefault("data", {})
    options_data.update(texts["options"])
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    """Update all three files."""
    english = language_texts(ENTITY_NAMES_EN, STATUS_STATES_EN, SUBENTRY_EN, OPTIONS_EN)
    german = language_texts(ENTITY_NAMES_DE, STATUS_STATES_DE, SUBENTRY_DE, OPTIONS_DE)
    merge_into(INTEGRATION_DIR / "strings.json", english)
    merge_into(INTEGRATION_DIR / "translations" / "en.json", english)
    merge_into(INTEGRATION_DIR / "translations" / "de.json", german)


if __name__ == "__main__":
    main()
