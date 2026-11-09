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
            "description": (
                "The charger will connect directly to Home Assistant (OCPP 1.6). "
                "The Easee cloud keeps working in parallel. Select the charger:"
            ),
            "data": {"serial": "Charger"},
        },
        "prerequisites": {
            "title": "Check requirements – {charger}",
            "description": (
                "{firmware_check} Firmware {firmware} (344 or newer required)\n"
                "{wifi_check} Connected via Wi-Fi (over cellular the charger cannot reach Home Assistant)\n"
                "{operator_check} Operator of the site: {operator} (must be Easee; change it in the Easee app if not)\n"
                "{circuit_check} No dynamic circuit limit below the fuse rating\n\n"
                "Important: while OCPP is active the charger only starts charging after Home Assistant "
                "accepted the RFID card. Make sure your cards are listed in the integration options "
                "(Configure → RFID cards)."
            ),
            "data": {"reset_circuit_limit": "Lift the dynamic circuit limit to the fuse rating"},
            "data_description": {
                "reset_circuit_limit": "Otherwise the circuit limit from the cloud keeps capping the OCPP limits."
            },
        },
        "address": {
            "title": "Address of Home Assistant – {charger}",
            "description": (
                "The charger connects to this address and appends /{serial}. It must be reachable from the "
                "charger's network: use the IP address or a name your router resolves (no .local names). "
                "Port 8123 is Home Assistant's own port, nothing else has to be opened. The connection is "
                "unencrypted (ws://) with a generated password, because Easee only accepts TLS certificates "
                "from a public CA."
            ),
            "data": {"ocpp_url": "OCPP address"},
        },
        "connection_failed": {
            "title": "{charger} did not connect",
            "description": (
                "The charger has not connected to {url} within 10 minutes. Possible causes: the address is "
                "not reachable from the charger's network (firewall, VLAN, wrong IP), the name cannot be "
                "resolved, or the charger is offline. Sometimes it just takes longer."
            ),
            "menu_options": {
                "connect": "Wait again",
                "address": "Change the address",
                "rollback": "Cancel and switch the charger back to cloud only",
                "finish": "Save anyway (the charger may connect later)",
            },
        },
    },
    "progress": {
        "wait_for_charger": (
            "OCPP is being enabled for {charger} via the Easee cloud. Waiting until the charger connects "
            "to {url}. This usually takes a few minutes (up to 10)."
        )
    },
    "error": {
        "invalid_url": "Enter a URL like ws://192.168.1.10:8123/api/easee/ocpp",
        "mdns_host": "The charger cannot resolve .local names; use the IP address or a name your router resolves.",
        "wss_not_supported": "wss:// needs a certificate from a public CA, which Home Assistant usually does not have. Use ws://.",
        "wrong_path": "The path must be /api/easee/ocpp (the charger appends its serial number).",
        "ocpp_forbidden": "The Easee cloud refused the change. Only the owner (or an admin) of the site may enable OCPP.",
        "ocpp_rejected": "The Easee cloud rejected the OCPP settings.",
        "cloud_unavailable": "The Easee cloud could not be reached. Try again later.",
        "integration_not_loaded": "The Easee integration is not loaded.",
    },
    "abort": {
        "no_unconfigured_chargers": "All chargers are already connected via OCPP.",
        "integration_not_loaded": "The Easee integration is not loaded.",
        "firmware_too_old": (
            "Firmware {firmware} does not support local OCPP (344 or newer required). "
            "Update the charger in the Easee app first."
        ),
        "rolled_back": "Cancelled. The charger is back on cloud only.",
        "ocpp_forbidden": "The Easee cloud refused the change. Only the owner (or an admin) of the site may change OCPP.",
        "ocpp_rejected": "The Easee cloud rejected the change.",
        "cloud_unavailable": "The Easee cloud could not be reached. Try again later.",
    },
}
SUBENTRY_DE: Texts = {
    "entry_type": "OCPP-Charger",
    "initiate_flow": {"user": "Charger per lokalem OCPP verbinden"},
    "step": {
        "user": {
            "title": "Charger per lokalem OCPP verbinden",
            "description": (
                "Der Charger verbindet sich direkt mit Home Assistant (OCPP 1.6). "
                "Die Easee-Cloud funktioniert parallel weiter. Wähle den Charger:"
            ),
            "data": {"serial": "Charger"},
        },
        "prerequisites": {
            "title": "Voraussetzungen prüfen – {charger}",
            "description": (
                "{firmware_check} Firmware {firmware} (mindestens 344)\n"
                "{wifi_check} Per WLAN verbunden (über Mobilfunk erreicht der Charger Home Assistant nicht)\n"
                "{operator_check} Betreiber des Standorts: {operator} (muss Easee sein; sonst in der Easee-App ändern)\n"
                "{circuit_check} Kein dynamisches Stromkreislimit unterhalb der Absicherung\n\n"
                "Wichtig: Solange OCPP aktiv ist, lädt der Charger erst, wenn Home Assistant die RFID-Karte "
                "freigegeben hat. Trage deine Karten in den Optionen der Integration ein "
                "(Konfigurieren → RFID-Karten)."
            ),
            "data": {"reset_circuit_limit": "Dynamisches Stromkreislimit auf die Absicherung anheben"},
            "data_description": {
                "reset_circuit_limit": "Sonst begrenzt das Stromkreislimit aus der Cloud weiterhin die OCPP-Limits."
            },
        },
        "address": {
            "title": "Adresse von Home Assistant – {charger}",
            "description": (
                "Der Charger verbindet sich mit dieser Adresse und hängt /{serial} an. Sie muss aus dem Netz "
                "des Chargers erreichbar sein: IP-Adresse oder ein Name, den dein Router auflöst (keine "
                ".local-Namen). Port 8123 ist der eigene Port von Home Assistant, es muss nichts weiter "
                "freigegeben werden. Die Verbindung ist unverschlüsselt (ws://) mit generiertem Passwort, "
                "weil Easee TLS nur mit Zertifikaten einer öffentlichen CA akzeptiert."
            ),
            "data": {"ocpp_url": "OCPP-Adresse"},
        },
        "connection_failed": {
            "title": "{charger} hat sich nicht verbunden",
            "description": (
                "Der Charger hat sich nicht innerhalb von 10 Minuten mit {url} verbunden. Mögliche Ursachen: "
                "Die Adresse ist aus dem Netz des Chargers nicht erreichbar (Firewall, VLAN, falsche IP), der "
                "Name lässt sich nicht auflösen, oder der Charger ist offline. Manchmal dauert es auch länger."
            ),
            "menu_options": {
                "connect": "Weiter warten",
                "address": "Adresse ändern",
                "rollback": "Abbrechen und Charger wieder nur über die Cloud betreiben",
                "finish": "Trotzdem speichern (der Charger verbindet sich evtl. später)",
            },
        },
    },
    "progress": {
        "wait_for_charger": (
            "OCPP wird für {charger} über die Easee-Cloud eingeschaltet. Warte, bis sich der Charger mit "
            "{url} verbindet. Das dauert meist ein paar Minuten (bis zu 10)."
        )
    },
    "error": {
        "invalid_url": "Gib eine URL wie ws://192.168.1.10:8123/api/easee/ocpp ein.",
        "mdns_host": "Der Charger kann keine .local-Namen auflösen; nutze die IP-Adresse oder einen Namen, den dein Router auflöst.",
        "wss_not_supported": "wss:// braucht ein Zertifikat einer öffentlichen CA, das Home Assistant meist nicht hat. Nutze ws://.",
        "wrong_path": "Der Pfad muss /api/easee/ocpp lauten (der Charger hängt seine Seriennummer an).",
        "ocpp_forbidden": "Die Easee-Cloud hat die Änderung abgelehnt. Nur der Besitzer (oder ein Admin) des Standorts darf OCPP einschalten.",
        "ocpp_rejected": "Die Easee-Cloud hat die OCPP-Einstellungen abgelehnt.",
        "cloud_unavailable": "Die Easee-Cloud ist nicht erreichbar. Versuche es später noch einmal.",
        "integration_not_loaded": "Die Easee-Integration ist nicht geladen.",
    },
    "abort": {
        "no_unconfigured_chargers": "Alle Charger sind bereits per OCPP verbunden.",
        "integration_not_loaded": "Die Easee-Integration ist nicht geladen.",
        "firmware_too_old": (
            "Firmware {firmware} unterstützt kein lokales OCPP (mindestens 344). "
            "Aktualisiere den Charger zuerst in der Easee-App."
        ),
        "rolled_back": "Abgebrochen. Der Charger läuft wieder nur über die Cloud.",
        "ocpp_forbidden": "Die Easee-Cloud hat die Änderung abgelehnt. Nur der Besitzer (oder ein Admin) des Standorts darf OCPP ändern.",
        "ocpp_rejected": "Die Easee-Cloud hat die Änderung abgelehnt.",
        "cloud_unavailable": "Die Easee-Cloud ist nicht erreichbar. Versuche es später noch einmal.",
    },
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
