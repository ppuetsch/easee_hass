"""Point an Easee charger at an OCPP server via the Easee cloud, or switch OCPP off again.

Development helper for the local OCPP feature; the integration's setup wizard does the
same from inside Home Assistant. Credentials come from EASEE_USERNAME / EASEE_PASSWORD.
With --password-from-ha the basic auth password is read from the charger's OCPP subentry
in Home Assistant (via SSH) and never printed.

    python scripts/easee_ocpp_connection.py EHDFQLBX --url ws://homeassistant.fritz.box:8123/api/easee/ocpp --password-from-ha
    python scripts/easee_ocpp_connection.py EHDFQLBX --off
    python scripts/easee_ocpp_connection.py EHDFQLBX --show
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
from typing import Any
import urllib.request

EASEE_API = "https://api.easee.com"
HA_SSH = os.environ.get("HA_SSH", "root@homeassistant.fritz.box")
HA_CONFIG_ENTRIES = "/config/.storage/core.config_entries"
MODE_DUAL_PROTOCOL = "DualProtocol"
MODE_OCPP_OFF = "OcppOff"

type Serial = str
type JsonObject = dict[str, Any]


def easee_request(
    method: str, path: str, token: str | None = None, body: JsonObject | None = None
) -> Any:
    """Call the Easee cloud API and return the parsed JSON (None for empty bodies)."""
    headers: dict[str, str] = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    payload = None
    if body is not None:
        # Easee answers 400 to a JSON content type without a body, so only send it with one.
        headers["Content-Type"] = "application/json"
        payload = json.dumps(body).encode()
    request = urllib.request.Request(
        EASEE_API + path, data=payload, headers=headers, method=method
    )
    with urllib.request.urlopen(request) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def login() -> str:
    """Return an access token for the account in EASEE_USERNAME / EASEE_PASSWORD."""
    credentials = {
        "userName": os.environ["EASEE_USERNAME"],
        "password": os.environ["EASEE_PASSWORD"],
    }
    token: str = easee_request("POST", "/api/accounts/login", body=credentials)[
        "accessToken"
    ]
    return token


def password_from_home_assistant(serial: Serial) -> str:
    """Read the basic auth password of the charger's OCPP subentry from HA storage."""
    storage = subprocess.run(
        ["ssh", HA_SSH, f"cat {HA_CONFIG_ENTRIES}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    for entry in json.loads(storage)["data"]["entries"]:
        for subentry in entry.get("subentries", []):
            if subentry.get("unique_id") == serial:
                password: str = subentry["data"]["ocpp_password"]
                return password
    raise SystemExit(f"No OCPP subentry for {serial} in Home Assistant")


def show_connection(token: str, serial: Serial) -> None:
    """Print the stored connection details (without secrets)."""
    details = (
        easee_request("GET", f"/local-ocpp/v1/connection-details/{serial}", token) or {}
    )
    url = details.get("websocketConnectionArgs", {}).get("url")
    print(
        f"{serial}: mode={details.get('connectivityMode')} url={url} chargePointId={details.get('chargePointId')}"
    )


def apply_connection(token: str, serial: Serial, connection: JsonObject) -> None:
    """Store the connection details and apply them to the charger."""
    stored = easee_request(
        "POST", f"/local-ocpp/v1/connection-details/{serial}", token, connection
    )
    easee_request(
        "POST",
        f"/local-ocpp/v1/connections/chargers/{serial}",
        token,
        {"version": stored["version"]},
    )


def parse_arguments() -> argparse.Namespace:
    """Command line."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("serial")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--url",
        help="OCPP server URL without the serial (the charger appends /<serial>)",
    )
    action.add_argument(
        "--off", action="store_true", help="switch OCPP off (cloud only)"
    )
    action.add_argument(
        "--show", action="store_true", help="only show the current setting"
    )
    parser.add_argument(
        "--password-from-ha",
        action="store_true",
        help="basic auth password from the HA subentry",
    )
    return parser.parse_args()


def main() -> None:
    """Show, enable or disable OCPP for one charger."""
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    arguments = parse_arguments()
    token = login()
    if arguments.off:
        apply_connection(token, arguments.serial, {"connectivityMode": MODE_OCPP_OFF})
    elif arguments.url:
        connection: JsonObject = {
            "connectivityMode": MODE_DUAL_PROTOCOL,
            "websocketConnectionArgs": {"url": arguments.url},
        }
        if arguments.password_from_ha:
            connection["basicAuthPassword"] = password_from_home_assistant(
                arguments.serial
            )
        apply_connection(token, arguments.serial, connection)
    show_connection(token, arguments.serial)


if __name__ == "__main__":
    main()
