"""A simulated Easee charger that talks OCPP 1.6J to the central system under test."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

from aiohttp import ClientWebSocketResponse, WSMsgType
from ocpp.routing import on
from ocpp.v16 import ChargePoint, call, call_result
from ocpp.v16.enums import Action

# Easee rejected every interval below 30 s in practice; the fake mimics that.
SMALLEST_ACCEPTED_SAMPLE_INTERVAL = 30
EASEE_UNKNOWN_KEYS = {"FreeCharging", "FreeChargingIdTag"}


class ClientConnection:
    """recv/send adapter for an aiohttp client websocket."""

    def __init__(self, websocket: ClientWebSocketResponse) -> None:
        """Wrap the websocket."""
        self._websocket = websocket

    async def recv(self) -> str:
        """Return the next text frame."""
        message = await self._websocket.receive()
        if message.type is not WSMsgType.TEXT:
            raise ConnectionError(message.type.name)
        return str(message.data)

    async def send(self, message: str) -> None:
        """Send a text frame."""
        await self._websocket.send_str(message)


@dataclass
class FakeChargerMemory:
    """What the central system did to the fake charger."""

    configuration: dict[str, str] = field(
        default_factory=lambda: {"MeterValueSampleInterval": "0", "HeartbeatInterval": "86400"}
    )
    charging_profiles: list[dict[str, Any]] = field(default_factory=list)
    triggered: list[str] = field(default_factory=list)


class FakeEaseeCharger(ChargePoint):
    """Answers the calls the central system sends, the way Easee does."""

    def __init__(self, serial: str, connection: ClientConnection) -> None:
        """Create the fake for one serial."""
        super().__init__(serial, connection, response_timeout=5)
        self.memory = FakeChargerMemory()

    @on(Action.change_configuration)
    def on_change_configuration(self, key: str, value: str, **kwargs: Any) -> call_result.ChangeConfiguration:
        """Reject short sample intervals like a real Easee."""
        too_short = key == "MeterValueSampleInterval" and int(value) < SMALLEST_ACCEPTED_SAMPLE_INTERVAL
        if too_short:
            return call_result.ChangeConfiguration(status="Rejected")
        self.memory.configuration[key] = value
        return call_result.ChangeConfiguration(status="Accepted")

    @on(Action.get_configuration)
    def on_get_configuration(self, key: list[str] | None = None, **kwargs: Any) -> call_result.GetConfiguration:
        """Return all keys, or the requested ones; Easee hides FreeCharging."""
        requested = key or list(self.memory.configuration)
        known = [name for name in requested if name in self.memory.configuration]
        unknown = [name for name in requested if name not in self.memory.configuration]
        return call_result.GetConfiguration(
            configuration_key=[
                {"key": name, "readonly": False, "value": self.memory.configuration[name]}
                for name in known
            ],
            unknown_key=unknown or None,
        )

    @on(Action.set_charging_profile)
    def on_set_charging_profile(
        self, connector_id: int, cs_charging_profiles: dict[str, Any], **kwargs: Any
    ) -> call_result.SetChargingProfile:
        """Remember the profile."""
        self.memory.charging_profiles.append(cs_charging_profiles)
        return call_result.SetChargingProfile(status="Accepted")

    @on(Action.get_composite_schedule)
    def on_get_composite_schedule(self, connector_id: int, duration: int, **kwargs: Any) -> call_result.GetCompositeSchedule:
        """Report the limit of the last profile."""
        if not self.memory.charging_profiles:
            return call_result.GetCompositeSchedule(status="Rejected")
        schedule = without_decimals(self.memory.charging_profiles[-1]["charging_schedule"])
        return call_result.GetCompositeSchedule(
            status="Accepted", connector_id=connector_id, charging_schedule=schedule
        )

    @on(Action.trigger_message)
    def on_trigger_message(self, requested_message: str, **kwargs: Any) -> call_result.TriggerMessage:
        """Accept every trigger."""
        self.memory.triggered.append(requested_message)
        return call_result.TriggerMessage(status="Accepted")

    async def boot(self) -> call_result.BootNotification:
        """Send a BootNotification."""
        return await self.call(
            call.BootNotification(
                charge_point_model="Home", charge_point_vendor="Easee", firmware_version="344"
            )
        )


def without_decimals(payload: Any) -> Any:
    """The ocpp library parses numbers as Decimal, which it cannot serialise again."""
    return json.loads(json.dumps(payload, default=float))


async def wait_until(condition: Any, timeout: float = 5.0) -> None:
    """Poll until condition() is truthy."""
    async with asyncio.timeout(timeout):
        while not condition():
            await asyncio.sleep(0.05)
