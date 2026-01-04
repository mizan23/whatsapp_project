📡 WhatsApp NOC Alarm Notification System

A production-grade WhatsApp alerting system for Network Operations Centers (NOC).
This project monitors alarms from a PostgreSQL database and sends real-time WhatsApp notifications with alarm and clear delays to avoid flapping.

The system is designed to be reliable, debounced, and WhatsApp-friendly, using a local WhatsApp Web sender service instead of cloud APIs.

🧩 Architecture Overview
PostgreSQL (SNMP / Alarm DB)
        ↓
Python Alarm Monitor
        ↓
Local WhatsApp Sender API
        ↓
WhatsApp (Web / Linked Device)

✨ Features

🚨 Alarm notification with configurable delay

✅ Alarm clear notification with separate delay

🧠 Alarm de-duplication & suppression logic

⏱ Poll-based monitoring (safe for production DBs)

📱 WhatsApp delivery using WhatsApp Web (no Twilio / Meta API)

🔁 Auto-reconnect WhatsApp session

🧾 systemd service support

🪵 Debug & structured logging

📂 Project Structure
.
├── whatsapp_msg_multiple_alarms.py   # Main alarm monitor (Python)
├── whatsapp_setup.sh                # WhatsApp sender installer
├── sender.js                        # WhatsApp Web sender (Node.js)
├── main.py                          # Optional / helper script
└── README.md

🛠️ Requirements
System

Ubuntu / Debian-based Linux

systemd

Internet access (for WhatsApp login)

Python

Python 3.8+

Packages:

pip install psycopg2 requests

Node.js

Node.js v22+ (installed automatically by setup script)

🔐 WhatsApp Sender (Web API)

This project uses a local WhatsApp Web sender powered by Baileys.

Why this approach?

❌ No Twilio cost

❌ No Meta WhatsApp Business approval

✅ Uses your real WhatsApp account

✅ Fast and reliable for NOC alerts

🚀 Installation
1️⃣ Install WhatsApp Sender Service
chmod +x whatsapp_setup.sh
./whatsapp_setup.sh


This will:

Install Node.js

Install dependencies

Create a systemd service

Expose a local API at http://127.0.0.1:3000

2️⃣ First-Time WhatsApp Login
cd ~/whatsapp-sender
node sender.js


📱 Scan the QR code using:

WhatsApp → Linked Devices → Link a device


Once connected:

sudo systemctl enable whatsapp-sender
sudo systemctl start whatsapp-sender

3️⃣ Health Check
curl http://127.0.0.1:3000/health


Expected response:

{ "whatsapp_ready": true }

🧠 Alarm Monitor Configuration

Edit whatsapp_msg_multiple_alarms.py:

Database
DB_CONFIG = {
    "host": "localhost",
    "database": "snmptraps",
    "user": "snmpuser",
    "password": "toor"
}

WhatsApp Target
WHATSAPP_API = "http://127.0.0.1:3000/send"
WHATSAPP_TO  = "8801870300750"  # no +

Timing Controls
POLL_INTERVAL     = 10   # seconds
ALARM_DELAY_SEC   = 30
CLEAR_DELAY_SEC   = 10

🧪 Alarm Logic
Alarm Trigger

Alarm must remain active for ALARM_DELAY_SEC

Prevents transient/flapping alarms

Clear Trigger

Alarm must remain cleared for CLEAR_DELAY_SEC

Suppression Logic

REM_SF alarms are suppressed if a LOCAL_FAULT exists for the same source

🏃 Running the Monitor
python3 whatsapp_msg_multiple_alarms.py


Example WhatsApp alert:

🚨 LOCAL_FAULT ALARM 🚨

Site       : DHAKA
Device     : Router
Source     : GE0/1
Severity   : CRITICAL
Alarm ID   : 18291
First Seen : 2025-01-01 12:30:00
Device Time: 2025-01-01 12:29:59

Link Down detected

🪵 Logs & Debugging
WhatsApp Sender Logs
journalctl -u whatsapp-sender -f

Python Monitor

Uses timestamped logs

Optional debug batching to reduce log noise

⚠️ Limitations

WhatsApp account must stay logged in

Single WhatsApp account per sender service

Poll-based DB monitoring (not event-driven)

🔮 Future Enhancements

Docker support

Multiple WhatsApp recipients

Severity-based routing

Grafana / Prometheus integration

Alarm acknowledgment support

Rate-limiting protection

🤝 Contributing

Pull requests are welcome.
Please open an issue for major changes or architectural discussions.
