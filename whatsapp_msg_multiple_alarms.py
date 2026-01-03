import psycopg2
import time
from datetime import datetime
import sys
import traceback
import requests

# =============================
# CONFIG
# =============================
POLL_INTERVAL = 10
DEBUG = True

ALARM_DELAY_SEC = 30
CLEAR_DELAY_SEC = 10
DEBUG_PRINT_INTERVAL = 10

WHATSAPP_API = "http://127.0.0.1:3000/send"
WHATSAPP_TO  = "8801870300750"   # no +

DB_CONFIG = {
    "host": "localhost",
    "database": "snmptraps",
    "user": "snmpuser",
    "password": "toor"
}

ALARM_CODES = ("LOCAL_FAULT", "REM_SF")

# =============================
# INIT
# =============================
print("=" * 80)
print(" WhatsApp NOC Alarm Monitor STARTING (WEB SENDER)")
print(f" Poll interval        : {POLL_INTERVAL}s")
print(f" Alarm delay          : {ALARM_DELAY_SEC}s")
print(f" Clear delay          : {CLEAR_DELAY_SEC}s")
print(f" Debug print interval : {DEBUG_PRINT_INTERVAL}s")
print("=" * 80, flush=True)

active_alarm_ids = set()
pending_alarm = {}
pending_clear = {}
alerted_alarm_ids = set()

debug_buffer = []
last_debug_flush = 0

# =============================
# LOGGING
# =============================
def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)

def debug_collect(msg):
    if DEBUG:
        debug_buffer.append(msg)

def debug_flush():
    global last_debug_flush
    now = time.monotonic()
    if now - last_debug_flush >= DEBUG_PRINT_INTERVAL and debug_buffer:
        print("=" * 60)
        for line in debug_buffer:
            log(line, "DEBUG")
        debug_buffer.clear()
        last_debug_flush = now

def error(msg):
    log(msg, "ERROR")

# =============================
# WHATSAPP SENDER (WEB)
# =============================
def send_whatsapp(message):
    log(f"WhatsApp send attempt | length={len(message)}")
    try:
        r = requests.post(
            WHATSAPP_API,
            json={"to": WHATSAPP_TO, "message": message},
            timeout=5
        )

        if r.status_code == 200:
            log("WhatsApp SENT (Web)")
        else:
            error(f"WhatsApp send failed: {r.text}")

    except Exception as e:
        error(f"WhatsApp exception: {e}")

# =============================
# MAIN LOOP
# =============================
def monitor():
    global active_alarm_ids

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        log("Database connected")
    except Exception:
        error("DB connection failed")
        sys.exit(1)

    while True:
        try:
            now_wall = datetime.now()
            now_mono = time.monotonic()

            debug_collect(f"Poll tick @ {now_wall}")
            debug_collect(f"Previous active_alarm_ids: {sorted(active_alarm_ids)}")
            debug_collect(f"Pending alarm timers: {list(pending_alarm.keys())}")
            debug_collect(f"Pending clear timers: {list(pending_clear.keys())}")
            debug_collect(f"Alerted alarms: {sorted(alerted_alarm_ids)}")

            cur.execute("""
                SELECT alarm_id, site, device_type, source, alarm_code,
                       severity, description, first_seen, device_time
                FROM active_alarms
                WHERE alarm_code IN %s;
            """, (ALARM_CODES,))

            rows = cur.fetchall()
            debug_collect(f"SQL returned {len(rows)} row(s)")

            current_alarm_ids = set()

            # Find LOCAL_FAULT sources
            critical_sources = set()
            for r in rows:
                _, site, device_type, source, alarm_code, *_ = r
                if alarm_code == "LOCAL_FAULT":
                    critical_sources.add((site, device_type, source))

            # Process active alarms
            for row in rows:
                (
                    alarm_id, site, device_type, source,
                    alarm_code, severity, description,
                    first_seen, device_time
                ) = row

                current_alarm_ids.add(alarm_id)
                key = (site, device_type, source)

                if alarm_code == "REM_SF" and key in critical_sources:
                    debug_collect(f"Suppress REM_SF alarm_id={alarm_id}")
                    continue

                if alarm_id not in active_alarm_ids and alarm_id not in pending_alarm:
                    pending_alarm[alarm_id] = now_mono
                    log(f"Alarm {alarm_id} ({alarm_code}) detected → start ALARM timer")

                if alarm_id in pending_alarm:
                    elapsed = int(now_mono - pending_alarm[alarm_id])
                    debug_collect(f"Alarm {alarm_id} active | alarm_timer={elapsed}s")

                    if elapsed >= ALARM_DELAY_SEC:
                        message = (
                            f"🚨 {alarm_code} ALARM 🚨\n\n"
                            f"Site       : {site}\n"
                            f"Device     : {device_type}\n"
                            f"Source     : {source}\n"
                            f"Severity   : {severity}\n"
                            f"Alarm ID   : {alarm_id}\n"
                            f"First Seen : {first_seen}\n"
                            f"Device Time: {device_time}\n\n"
                            f"{description}"
                        )
                        send_whatsapp(message)
                        alerted_alarm_ids.add(alarm_id)
                        del pending_alarm[alarm_id]

            # Detect cleared alarms
            cleared_ids = active_alarm_ids - current_alarm_ids
            debug_collect(f"Detected cleared alarms: {sorted(cleared_ids)}")

            for alarm_id in cleared_ids:
                if alarm_id not in alerted_alarm_ids:
                    debug_collect(f"Skip CLEAR for alarm_id={alarm_id}")
                    continue
                if alarm_id not in pending_clear:
                    pending_clear[alarm_id] = now_mono
                    log(f"Alarm {alarm_id} cleared → start CLEAR timer")

            # Process clear timers
            for alarm_id in list(pending_clear.keys()):
                if alarm_id in current_alarm_ids:
                    del pending_clear[alarm_id]
                    continue

                elapsed = int(now_mono - pending_clear[alarm_id])
                debug_collect(f"Alarm {alarm_id} cleared | clear_timer={elapsed}s")

                if elapsed >= CLEAR_DELAY_SEC:
                    clear_message = (
                        "✅ ALARM CLEARED ✅\n\n"
                        f"Alarm ID    : {alarm_id}\n"
                        f"Cleared Time: {datetime.now()}"
                    )
                    send_whatsapp(clear_message)
                    pending_clear.pop(alarm_id, None)
                    alerted_alarm_ids.discard(alarm_id)

            active_alarm_ids = current_alarm_ids
            debug_collect(f"Updating active_alarm_ids → {sorted(active_alarm_ids)}")

            debug_flush()
            time.sleep(POLL_INTERVAL)

        except Exception:
            error("Unhandled exception in monitor loop")
            traceback.print_exc()
            time.sleep(POLL_INTERVAL)

# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    monitor()
