# 📡 WhatsApp NOC Alarm Notification System

A **production-ready WhatsApp alerting system** for Network Operations Centers (NOC).  
This project monitors alarms from a **PostgreSQL database** and sends **real-time WhatsApp notifications** with configurable alarm and clear delays to prevent flapping.

The system uses a **local WhatsApp Web sender service**, avoiding paid APIs and approval requirements.

---

## 🧩 Architecture

PostgreSQL (Alarm DB)
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

- 🚨 Alarm notification with delay
- ✅ Alarm clear notification with delay
- 🧠 Alarm de-duplication & suppression
- ⏱ Poll-based monitoring
- 📱 WhatsApp Web delivery (no Twilio / Meta API)
- 🔁 Auto-reconnect WhatsApp session
- 🧾 systemd service support
- 🪵 Debug & structured logging

---

## 📂 Project Structure

.
├── whatsapp_msg_multiple_alarms.py # Main alarm monitor
├── whatsapp_setup.sh # WhatsApp sender installer
├── sender.js # WhatsApp Web sender (Node.js)
├── main.py # Optional helper script
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
- Python 3.8+
- Dependencies:
  ```bash
  pip install psycopg2 requests
Node.js
Node.js v22+ (installed automatically)

🚀 Installation
1️⃣ Install WhatsApp Sender Service
bash
Copy code
chmod +x whatsapp_setup.sh
./whatsapp_setup.sh
This installs Node.js, dependencies, and creates a systemd service.

2️⃣ First-Time WhatsApp Login
bash
Copy code
cd ~/whatsapp-sender
node sender.js
Scan the QR code using:

css
Copy code
WhatsApp → Linked Devices → Link a device
After successful login:

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
{ "whatsapp_ready": true }
⚙️ Alarm Monitor Configuration
Edit whatsapp_msg_multiple_alarms.py:

Database Settings
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
WHATSAPP_TO  = "8801870300750"  # no +
Timing Controls
python
Copy code
POLL_INTERVAL   = 10
ALARM_DELAY_SEC = 30
CLEAR_DELAY_SEC = 10
🧠 Alarm Logic
Alarms must persist for ALARM_DELAY_SEC before notification

Clears must persist for CLEAR_DELAY_SEC

REM_SF alarms are suppressed if a LOCAL_FAULT exists for the same source

Prevents alarm flapping and duplicates

▶️ Running the Monitor
bash
Copy code
python3 whatsapp_msg_multiple_alarms.py
🪵 Logs
WhatsApp Sender
bash
Copy code
journalctl -u whatsapp-sender -f
Python Monitor
Timestamped logs

Optional debug batching

⚠️ Limitations
WhatsApp account must stay logged in

Single WhatsApp account per sender

Poll-based DB monitoring

🔮 Future Enhancements
Docker / Docker Compose

Multiple recipients

Severity-based routing

Grafana / Prometheus integration

Alarm acknowledgment support

🤝 Contributing
Pull requests are welcome.
Please open an issue for major changes.

