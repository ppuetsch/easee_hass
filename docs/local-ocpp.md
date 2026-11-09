# Local OCPP (Easee charger ↔ Home Assistant)

With local OCPP the charger connects **directly to Home Assistant** (OCPP 1.6J). The Easee cloud
keeps working in parallel (`DualProtocol`), so all existing cloud entities stay. You additionally get
fast local measurements, local current limits that work without the cloud, every OCPP setting
of the charger, and RFID authorization decided by Home Assistant.

## Requirements
- Easee charger with firmware **344 or newer**, connected via **Wi-Fi** (over cellular it cannot
  reach Home Assistant).
- The site's operator must be **Easee** (Easee app → site settings).
- You are owner or admin of the site (the cloud refuses the change otherwise).
- Home Assistant must be reachable from the charger's network on its normal port (8123).
  No extra port, add-on or reverse proxy is needed: the endpoint is part of Home Assistant itself.

## Setup
1. Settings → Devices & services → Easee → **Connect charger via local OCPP**.
2. Pick the charger. The wizard checks firmware, Wi-Fi, operator and a dynamic circuit limit
   (which it can lift for you, otherwise it keeps capping the OCPP limits).
3. Confirm the address. It is suggested from Home Assistant's internal URL; use an IP address or a
   name your router resolves. `.local` names do not work (the charger cannot resolve mDNS).
4. The wizard enables OCPP via the Easee cloud and waits until the charger connects (usually a few
   minutes). If it does not connect within 10 minutes you can wait again, change the address,
   roll back to cloud only, or save anyway.

Repeat for every charger; each one is a separate entry under the integration and gets its own
generated password. The address can be changed later via **Reconfigure** on that entry.

### RFID cards – important
While OCPP is active **the charger asks Home Assistant for every card** and only charges after
Home Assistant accepted it. Add your cards under the integration's **Configure → RFID cards**,
or press **OCPP learn next RFID card** and hold the card to the charger within two minutes.
Cards paired in the Easee app are not known to Home Assistant (the cloud API offers no card list).
Every decision fires the event `easee_ocpp_authorize` (`serial`, `id_tag`, `accepted`).

## Entities (per charger, prefixed "OCPP")
- **Sensors:** status, power, energy meter (energy dashboard), session energy/start, current and
  voltage per phase, offered current, effective charging limit, temperature, last RFID card
  (attribute `accepted`), error codes, transaction id, last message, meter interval, firmware.
- **Binary sensors:** connected, session active, charging.
- **Number:** max current (ChargePointMaxProfile; 0 A pauses; re-sent after every reconnect).
- **Switches:** available (ChangeAvailability), charge (RemoteStart/RemoteStop).
- **Buttons:** restart, reboot, unlock cable, refresh, learn next RFID card.
- **Every configuration key** of the charger: writable booleans → switch, numbers → number,
  other values → text (category *configuration*); read-only keys → diagnostic sensors (disabled
  by default). On Easee this includes e.g. `LightIntensity`, `HeartbeatInterval`,
  `MeterValueSampleInterval` (Easee accepts 30 s and more), `LocalAuthorizeOffline`,
  `LocalAuthListEnabled`, `FreeCharging`.

## Actions
`easee.ocpp_get_configuration`, `easee.ocpp_change_configuration`, `easee.ocpp_set_charging_profile`,
`easee.ocpp_clear_charging_profile`, `easee.ocpp_get_composite_schedule`, `easee.ocpp_trigger_message`,
`easee.ocpp_send_local_list` (cards accepted while Home Assistant is unreachable, max. 10 on Easee),
`easee.ocpp_get_local_list_version`.

## Repairs
Home Assistant raises a repair issue when a charger has been disconnected for 15 minutes, keeps
failing authentication, or its stored address no longer resolves to Home Assistant. The fix
re-applies the connection (address + password) via the Easee cloud.

## Removing
Deleting a charger's OCPP entry switches the charger back to cloud only, as long as it still points
at Home Assistant. Without this the charger would keep waiting for Home Assistant to authorize.

## Limitations (measured on an Easee Home)
- `ws://` only: Easee accepts TLS certificates from a public CA only; the connection is protected
  by a generated basic auth password (security profile 1). Keep it in your home network.
- Easee supports the profiles Core, SmartCharging, RemoteTrigger and LocalAuthListManagement; no
  firmware update, diagnostics upload or reservation via OCPP. `DataTransfer` and `ClearCache` are
  not supported.
- Charging limits are in amperes; the charger answers at most one key per `GetConfiguration`.
- See `local-ocpp-easee-inventory.md` for the full configuration inventory of a real charger.
