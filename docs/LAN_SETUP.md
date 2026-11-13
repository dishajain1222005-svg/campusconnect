# CampusConnect – LAN Setup Guide

## Networking Concepts (plain language)

| Term | What it means |
|------|---------------|
| **IP address** | A number that identifies a device on a network, like a postal address. Example: `192.168.1.5` |
| **Subnet** | The local network. All devices on the same subnet can talk to each other. |
| **Port** | A numbered door on a device. CampusConnect uses port **5000**. |
| **HTTP** | The language browsers use to request web pages. |
| **0.0.0.0** | Means "listen on ALL network interfaces". The app will be reachable on every IP the server has. |
| **127.0.0.1 / localhost** | Only reachable from the same machine. Other devices cannot use this. |
| **LAN IPv4** | The real IP other devices use to find this machine on the local network. |
| **TCP** | The transport protocol. HTTP runs over TCP. |
| **Socket** | A TCP connection is a "socket" — think of it as a phone call between two programs. |

---

## Step 1 – Find the server's LAN IP

**Option A – batch file:**
```bat
scripts\show_ip.bat
```

**Option B – manual:**
```bat
ipconfig
```
Look for the **Wi-Fi** (or Wireless LAN) adapter and note the **IPv4 Address**, e.g. `192.168.1.42`.

---

## Step 2 – Add Windows Firewall rule (run once, as Administrator)

By default Windows blocks incoming connections on port 5000. Add a rule:

```powershell
# Run PowerShell as Administrator
New-NetFirewallRule `
    -DisplayName "CampusConnect-Port-5000" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5000 `
    -Action Allow `
    -Profile Private `
    -RemoteAddress LocalSubnet `
    -Description "CampusConnect LAN demo"
```

Or just double-click `scripts\add_firewall_rule.ps1` (right-click → Run as Administrator).

**To remove the rule afterwards:**
```powershell
Remove-NetFirewallRule -DisplayName "CampusConnect-Port-5000"
```

---

## Step 3 – Set the Wi-Fi network profile to Private

If the network profile is "Public", the firewall Private rule won't apply.

```powershell
# Replace "Wi-Fi" with your adapter name if different
Set-NetConnectionProfile -InterfaceAlias "Wi-Fi" -NetworkCategory Private
```

Or: Settings → Network & Internet → Wi-Fi → click your network → Set "Network profile type" to Private.

---

## Step 4 – Test connectivity

**From another device on the same Wi-Fi, open a browser and go to:**
```
http://192.168.x.x:5000
```
(replace with your actual LAN IP from Step 1)

**To test from PowerShell on another Windows machine:**
```powershell
Test-NetConnection 192.168.x.x -Port 5000
```
Look for `TcpTestSucceeded : True`.

**To ping the server:**
```bat
ping 192.168.x.x
```

---

## Setup Scenarios

### A – Router without internet (classroom router)
- Connect the server laptop and all client devices to the router's Wi-Fi.
- The router assigns IP addresses (DHCP). Note the server's IP with `ipconfig`.
- No internet is required. Everything stays local.

### B – Windows 11 Mobile Hotspot
- On the server laptop: Settings → Network & Internet → Mobile hotspot → turn ON.
- Other devices connect to this hotspot by name.
- The server's IP on the hotspot is usually **192.168.137.1**.
- Students connect to `http://192.168.137.1:5000`.
- Advantage: no Wi-Fi client isolation — devices can always reach the server.

### C – Smartphone hotspot
- Turn on hotspot on a phone. Connect the laptop and other devices to it.
- Find the laptop's IP with `ipconfig` (look for the hotspot adapter).
- Note: some phone hotspots enable AP (client) isolation — if devices can't
  reach each other, switch to Windows Mobile Hotspot (Option B).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Connection refused (port 5000) | Firewall blocking | Run `add_firewall_rule.ps1` as admin |
| Connection timed out | Wrong IP, or server not running | Check IP with `show_ip.bat`, verify server is running |
| Works on localhost but not from phone | Network profile is "Public" | Set to Private (Step 3) |
| IP changed after reconnecting | DHCP assigned a new IP | Re-run `show_ip.bat` and share the new URL |
| VirtualBox / WSL / Hyper-V adapter appears in `ipconfig` | Virtual adapter listed first | Use the IP under the physical Wi-Fi adapter |
| Devices can't reach each other (phone hotspot) | AP isolation enabled | Use Windows Mobile Hotspot instead |
| VPN is running | VPN changes routing | Disconnect VPN on the server while running CampusConnect |

---

## Request-response cycle (how it works)

```
Student's browser                 CampusConnect Server (your laptop)
──────────────────                ──────────────────────────────────
1. Types: http://192.168.1.42:5000/login
2. Browser creates a TCP connection to 192.168.1.42 on port 5000
3. Sends: GET /login HTTP/1.1
                            ←─── 4. Flask receives the request
                            ←─── 5. Renders login.html template
6. Browser receives HTML   ─────  6. Sends HTTP 200 response with HTML
7. Displays the page
```

---

## Important disclaimers

- The Flask development server (`python run.py`) is **not** for production use.
  It is suitable for a controlled classroom demo.
- For better stability with 20+ simultaneous users, use Waitress:
  `python run.py --waitress`
- Do **not** expose this server to the internet.
- Do **not** disable Windows Firewall entirely — only the specific rule above is needed.
