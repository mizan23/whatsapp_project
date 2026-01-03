#!/bin/bash
set -e

APP_DIR="$HOME/whatsapp-sender"
SERVICE_NAME="whatsapp-sender"

echo "🚀 Installing WhatsApp Sender (Production Mode)"

# ---------------- SYSTEM ----------------
sudo apt update -y
sudo apt install -y curl ca-certificates gnupg

# ---------------- NODE.JS ----------------
if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt install -y nodejs
fi

node -v
npm -v

# ---------------- PROJECT ----------------
mkdir -p "$APP_DIR"
cd "$APP_DIR"

cat > package.json <<'EOF'
{
  "name": "whatsapp-sender",
  "version": "1.0.0",
  "type": "module",
  "main": "sender.js",
  "scripts": {
    "start": "node sender.js"
  }
}
EOF

npm install @whiskeysockets/baileys express pino qrcode-terminal

# ---------------- sender.js ----------------
cat > sender.js <<'EOF'
import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason
} from "@whiskeysockets/baileys";
import express from "express";
import Pino from "pino";
import qrcode from "qrcode-terminal";

const app = express();
app.use(express.json());

const logger = Pino({ level: "silent" });

let sock = null;
let isReady = false;

async function startSock() {
  const { state, saveCreds } = await useMultiFileAuthState("./auth");

  sock = makeWASocket({
    auth: state,
    logger
  });

  isReady = false;

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("\n📱 Scan this QR code with WhatsApp (Linked Devices):\n");
      qrcode.generate(qr, { small: true });
    }

    if (connection === "open") {
      isReady = true;
      console.log("✅ WhatsApp connected and READY");
    }

    if (connection === "close") {
      isReady = false;
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !==
        DisconnectReason.loggedOut;

      if (shouldReconnect) {
        console.log("🔁 Reconnecting WhatsApp...");
        setTimeout(startSock, 3000);
      } else {
        console.log("🚫 Logged out from WhatsApp");
      }
    }
  });
}

app.post("/send", async (req, res) => {
  const { to, message } = req.body;

  if (!to || !message)
    return res.status(400).json({ error: "missing to or message" });

  if (!sock || !isReady)
    return res.status(503).json({ error: "whatsapp_not_ready" });

  await sock.sendMessage(`${to}@s.whatsapp.net`, { text: message });
  console.log(`📤 Sent WhatsApp to ${to}`);
  res.json({ status: "sent" });
});

app.get("/health", (_, res) => {
  res.json({ whatsapp_ready: isReady });
});

app.listen(3000, () => {
  console.log("🚀 WhatsApp sender listening on http://127.0.0.1:3000");
});

startSock();
EOF

# ---------------- systemd ----------------
sudo tee /etc/systemd/system/${SERVICE_NAME}.service >/dev/null <<EOF
[Unit]
Description=WhatsApp Sender Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/node sender.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "✅ Installed"
echo ""
echo "➡️ FIRST RUN (scan QR):"
echo "   cd $APP_DIR && node sender.js"
echo ""
echo "➡️ AFTER QR SCAN:"
echo "   sudo systemctl enable ${SERVICE_NAME}"
echo "   sudo systemctl start ${SERVICE_NAME}"



echo "✅ Installed"
echo ""
echo "➡️ FIRST RUN (scan QR):"
echo "   cd $APP_DIR && node sender.js"
echo ""
echo "➡️ AFTER QR SCAN (run in background):"
echo "   sudo systemctl enable ${SERVICE_NAME}"
echo "   sudo systemctl start ${SERVICE_NAME}"
echo ""
echo "ℹ️ Logs:"
echo "   journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "-----------------------------------------"
echo "API TEST (MANUAL – DO NOT AUTO RUN)"
echo "-----------------------------------------"
echo "curl -X POST http://127.0.0.1:3000/send \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"to\":\"8801870300750\",\"message\":\"Running in background 🚀\"}'"
echo ""
echo "Health check:"
echo "curl http://127.0.0.1:3000/health"
