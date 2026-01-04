# WhatsApp NOC Alarm Monitor

This project provides an **end-to-end WhatsApp alerting solution for NOC alarms** using:

- **Python** to monitor alarms from a PostgreSQL database
- **Node.js + Baileys** to send WhatsApp messages via WhatsApp Web
- **systemd** for running the WhatsApp sender as a background service

---

## Architecture Overview

```
PostgreSQL (SNMP Traps DB)
        |
        v
Python Alarm Monitor
(whatsapp_msg_multiple_alarms.py)
        |
        v   HTTP (JSON)
Local WhatsApp API
(Node.js / Baileys)
        |
        v
WhatsApp User / Group
```

---

## Components

### 1. Python Alarm Monitor

**File:** `whatsapp_msg_multiple_alarms.py`

**Responsibilities:**
- Polls the `active_alarms` table in PostgreSQL
- Applies alarm & clear delays to avoid flapping
- Suppresses `REM_SF` alarms when `LOCAL_FAULT` exists
- Sends alarm and clear notifications to WhatsApp

**Key Features:**
- Configurable polling interval
- Alarm & clear delay timers
- Alarm suppression logic
- Debug buffering to reduce console noise

---

### 2. WhatsApp Sender Service

**Installed by:** `whatsapp_setup.sh`

**Responsibilities:**
- Runs a local HTTP API on `127.0.0.1:3000`
- Connects to WhatsApp Web using QR code
- Sends messages via Baileys library
- Runs persistently using `systemd`

**Endpoints:**
- `POST /send` → Send WhatsApp message
- `GET  /health` → WhatsApp readiness check

---

## Prerequisites

### System
- Ubuntu 20.04+ (recommended)
- Internet access
- WhatsApp account (mobile app)

### Software
- Python 3.9+
- PostgreSQL
- Node.js 22+
- npm

### Python Dependencies
```
pip install psycopg2 requests
```

---

## Installation

### 1. Install WhatsApp Sender (Node.js)

```
chmod +x whatsapp_setup.sh
./whatsapp_setup.sh
```

**First Run (QR Scan):**
```
cd ~/whatsapp-sender
node sender.js
```

Scan the QR code using:
**WhatsApp → Linked Devices → Link a device**

After successful login:

```
sudo systemctl enable whatsapp-sender
sudo systemctl start whatsapp-sender
```

Check logs:
```
journalctl -u whatsapp-sender -f
```

---

### 2. Configure Python Alarm Monitor

Edit configuration inside `whatsapp_msg_multiple_alarms.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "snmptraps",
    "user": "snmpuser",
    "password": "toor"
}

WHATSAPP_API = "http://127.0.0.1:3000/send"
WHATSAPP_TO  = "8801870300750"
```

Adjust timing if needed:
```python
POLL_INTERVAL = 10
ALARM_DELAY_SEC = 30
CLEAR_DELAY_SEC = 10
```

---

## Running the Alarm Monitor

```
python3 whatsapp_msg_multiple_alarms.py
```

For production, run using:
- `tmux`
- `screen`
- or create a `systemd` service

---

## WhatsApp Message Examples

**Alarm:**
```
🚨 LOCAL_FAULT ALARM 🚨

Site       : SITE_A
Device     : OLT
Source     : PORT-1
Severity   : CRITICAL
Alarm ID   : 12345
First Seen : 2025-01-01 10:00:00
Device Time: 2025-01-01 09:59:58
```

**Clear:**
```
✅ ALARM CLEARED ✅

Alarm ID    : 12345
Cleared Time: 2025-01-01 10:05:00
```

---

## Health Check

```
curl http://127.0.0.1:3000/health
```

Response:
```json
{ "whatsapp_ready": true }
```

---

## Security Notes

- WhatsApp authentication files are stored locally (`~/whatsapp-sender/auth`)
- Do **NOT** expose port `3000` externally
- Protect database credentials

---

## Troubleshooting

**WhatsApp not sending**
- Check `/health` endpoint
- Ensure QR was scanned
- Review `journalctl -u whatsapp-sender`

**No alarms**
- Verify `active_alarms` table
- Confirm alarm codes exist
- Enable `DEBUG = True`

---

## License

Internal / Private Use  
No warranty provided.

---

## Author

NOC Automation Script  
Designed for carrier-grade alarm monitoring 🚀
