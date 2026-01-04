# 📡 WhatsApp NOC Alarm Notification System

A **production-ready WhatsApp alerting system** for Network Operations Centers (NOC).

This project monitors alarms from a **PostgreSQL database** and sends **real-time WhatsApp notifications** with configurable alarm and clear delays to prevent alarm flapping.

The system uses a **local WhatsApp Web sender service**, avoiding paid APIs and WhatsApp Business approval requirements.

---

## 🧩 Architecture

PostgreSQL (Alarm Database)
↓
Python Alarm Monitor
↓
Local WhatsApp Sender API
↓
WhatsApp (Linked Device)

yaml
Copy code

---

## ✨ Features

- 🚨 Alarm notification with configurable delay
- ✅ Alarm clear notification with separate delay
- 🧠 Alarm de-duplication and suppression logic
- ⏱ Poll-based monitoring (safe for production DBs)
- 📱 WhatsApp Web delivery (no Twilio / Meta API)
- 🔁 Automatic WhatsApp reconnection
- 🧾 systemd service support
- 🪵 Structured and debug logging

---

## 📂 Project Structure

.
├── whatsapp_msg_multiple_alarms.py # Main alarm monitoring script
├── whatsapp_setup.sh # WhatsApp sender installer
├── sender.js # WhatsApp Web sender (Node.js)
├── main.py # Optional helper / test script
└── README.md

yaml
Copy code

---

## 🛠️ Requirements

### System
- Ubuntu / Debian-based Linux
- systemd
- Internet access

### Python
- Python 3.8 or higher
- Required packages:
  ```bash
  pip install psycopg2 requests
Node.js
Node.js v22 or higher
(Installed automatically by the setup script)

🚀 Installation
1️⃣ Install WhatsApp Sender Service
bash
Copy code
chmod +x whatsapp_setup.sh
./whatsapp_setup.sh
This will:

Install Node.js

Install required Node packages

Create a systemd service

Expose a local API at http://127.0.0.1:3000

2️⃣ First-Time WhatsApp Login
Run the sender manually once:

bash
Copy code
cd ~/whatsapp-sender
node sender.js
Scan the QR code using:

css
Copy code
WhatsApp → Linked Devices → Link a device
After successful login, enable background service:

bash
Copy code
sudo systemctl enable whatsapp-sender
sudo systemctl start whatsapp-sender
3️⃣ Health Check
bash
Copy code
curl http://127.0.0.1:3000/health
Expected response:

json
Copy code
{
  "whatsapp_ready": true
}
⚙️ Alarm Monitor Configuration
Edit whatsapp_msg_multiple_alarms.py.

Database Configuration
python
Copy code
DB_CONFIG = {
    "host": "localhost",
    "database": "snmptraps",
    "user": "snmpuser",
    "password": "toor"
}
WhatsApp Target
python
Copy code
WHATSAPP_API = "http://127.0.0.1:3000/send"
WHATSAPP_TO  = "8801870300750"  # country code only, no "+"
Timing Controls
python
Copy code
POLL_INTERVAL   = 10   # seconds
ALARM_DELAY_SEC = 30
CLEAR_DELAY_SEC = 10
🧠 Alarm Logic
Alarm must remain active for ALARM_DELAY_SEC before notification

Clear must remain inactive for CLEAR_DELAY_SEC

REM_SF alarms are suppressed if a LOCAL_FAULT exists for the same source

Prevents duplicate and flapping alerts

▶️ Running the Alarm Monitor
bash
Copy code
python3 whatsapp_msg_multiple_alarms.py
🪵 Logs & Debugging
WhatsApp Sender Logs
bash
Copy code
journalctl -u whatsapp-sender -f
Python Monitor Logs
Timestamped output

Optional debug batching to reduce noise

⚠️ Limitations
WhatsApp account must stay logged in

One WhatsApp account per sender service

Poll-based monitoring (not event-driven)

🔮 Future Enhancements
Docker / Docker Compose support

Multiple WhatsApp recipients

Severity-based routing

Grafana / Prometheus integration

Alarm acknowledgment workflow

🤝 Contributing
Pull requests are welcome.
Please open an issue for major changes or feature discussions.
