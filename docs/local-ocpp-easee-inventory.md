# Easee charger: OCPP inventory (measured 2026-11-09, firmware with DualProtocol)

Read from a real Easee Home (EHDFQLBX) connected to `ws://<HA>:8123/api/easee/ocpp`.

## Connection
- The charger appends `/<serial>` to the configured URL (stored as `.../api/easee/ocpp/EHDFQLBX`).
- Security profile 1 (ws + basic auth, user = serial) works through Home Assistant's own HTTP server.
- After applying the cloud configuration it took ~5 minutes until the charger connected.
- The Easee cloud answers HTTP 400 to a GET with `Content-Type: application/json` and no body.

## GetConfiguration (all keys)
| Key | RW | Value |
|---|---|---|
| AuthorizationCacheEnabled | RO | True |
| ClockAlignedDataInterval | RW | 0 |
| GetConfigurationMaxKeys | RO | 1 (!) |
| HeartbeatInterval | RW | 300 |
| LightIntensity | RW | 25 (Easee specific) |
| LocalAuthorizeOffline | RW | True |
| MeterValuesAlignedData | RW | Current.Import,Current.Offered,Energy.Active.Import.Register,Power.Active.Import,Temperature,Voltage |
| MeterValuesSampledData | RW | same as above |
| MeterValueSampleInterval | RW | 30 (10 and 15 are rejected) |
| NumberOfConnectors | RO | 1 |
| StopTransactionOnEVSideDisconnect | RO | True |
| StopTransactionOnInvalidId | RO | True |
| SupportedFeatureProfiles | RO | Core,LocalAuthListManagement,SmartCharging,RemoteTrigger |
| UnlockConnectorOnEVSideDisconnect | RW | False |
| LocalAuthListEnabled | RW | False |
| LocalAuthListMaxLength | RO | 10 |
| SendLocalListMaxLength | RO | 10 |
| ChargeProfileMaxStackLevel | RO | 10 |
| ChargingScheduleAllowedChargingRateUnit | RO | Current |
| ChargingScheduleMaxPeriods | RO | 24 |
| MaxChargingProfilesInstalled | RO | 10 |

Hidden keys (only by name, one per request): `FreeCharging` = False. `FreeChargingIdTag` was not returned
when requested together with FreeCharging (max 1 key per request).

## Not supported (no feature profile)
FirmwareManagement (UpdateFirmware, GetDiagnostics), Reservation (ReserveNow, CancelReservation).
Easee documents DataTransfer and ClearCache as unsupported.
