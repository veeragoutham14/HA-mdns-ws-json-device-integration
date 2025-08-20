# HA-mdns-ws-json-device-integration
Home Assistant integration framework for devices discoverable via mDNS and communicating over WebSocket with JSON payloads.

# HA-mdns-ws-json-device-integration
Home Assistant integration framework for devices discoverable via mDNS and communicating over WebSocket with JSON payloads.

## Installation

### Option A — Install via HACS (recommended)

1. Open Home Assistant → **HACS** (left sidebar).
2. Click the **⋮ (menu)** in the top-right → **Custom repositories**.
3. In the dialog:
   - Paste **this repository’s URL**.
   - Set **Category** to `Integration`.
   - Click **Add**.
4. Go back to **HACS → Integrations**, find this repo, **Install**, then **Restart Home Assistant**.
5. Add the integration: **Settings → Devices & Services → Add Integration → KaVo Integration**  
   (or wait for Zeroconf discovery if offered).

**Repository layout required by HACS:**
custom_components/
└── KaVo_Integration/
├── init.py
├── manifest.json
├── config_flow.py
├── const.py
├── calendar.py
├── sensor.py
├── switch.py
├── websocket_client.py
├── translations/
└── ... (other platform files)

pgsql
Kopieren
Bearbeiten

**Keep `hacs.json` in sync** (when distributing via HACS):
```json
{
  "name": "KaVo_Integration",
  "render_readme": true,
  "homeassistant": "2024.8.0",
  "hacs": "2.0.0"
}
Update "homeassistant" when you use newer HA APIs.

Update "hacs" if your repo requires a newer HACS version.

Option B — Manual install (VS Code add-on)
Open the VS Code add-on in Home Assistant.

Copy only the folder KaVo_Integration/ into:

swift
Kopieren
Bearbeiten
/config/custom_components/KaVo_Integration/
(create custom_components/ if it doesn’t exist).

Restart Home Assistant.

Add the integration: Settings → Devices & Services → Add Integration → KaVo Integration.

Features
Zeroconf/mDNS discovery for plug-and-play device onboarding.

WebSocket transport with JSON payloads for low-latency, bidirectional updates.

Automatic creation of entities (e.g., sensors, calendars, switches) after connection.

Designed to integrate with CONNECTbase device software.

Troubleshooting
Integration not found in “Add Integration”
Restart HA, then check Settings → System → Logs for errors from custom_components.kavo_integration.

Duplicate/unavailable entities after renaming
Ensure your entities use a stable unique_id (not the display name). If you changed schemes, implement an entity registry migration.

Manual install not loading
Verify the path is exactly /config/custom_components/KaVo_Integration/ and manifest.json is present. Restart HA.

