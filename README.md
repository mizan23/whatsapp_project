# 📩 WhatsApp Message Scheduler using Twilio (Python)

This project is a **Python-based WhatsApp message scheduler** built using the **Twilio WhatsApp API**.  
It allows a user to schedule a WhatsApp message to be sent to an **individual recipient** at a **specific date and time**.

> ⚠️ **Note**  
> WhatsApp group messaging is **not supported** by Twilio or WhatsApp APIs.  
> This script works **only for one-to-one WhatsApp messages**.

---

## ✨ Features

- Send WhatsApp messages using Twilio  
- Schedule messages for a future date and time  
- Simple CLI-based user input  
- Error handling for failed message delivery  
- Clean and readable Python code  

---

## 🛠️ Requirements

### Python Version
- Python **3.7 or higher**

### Twilio Account
- A Twilio account  
- WhatsApp Sandbox enabled **or** an approved WhatsApp Business number  

### Python Libraries
Install required dependencies:

```bash
pip install twilio
```

---

## 🔐 Twilio Credentials Setup

You must provide the following credentials from your **Twilio Console**:

- **Account SID**
- **Auth Token**
- **Twilio WhatsApp Number**

Example:

```python
account_sid = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
auth_token = 'your_auth_token_here'
from_number = '+14155238886'
```

> ⚠️ **Security Warning**  
> Never commit real credentials to GitHub.  
> Use **environment variables** or `.env` files in production.

---

## 🚀 How to Run the Script

### Clone the Repository

```bash
git clone https://github.com/your-username/whatsapp-message-scheduler.git
cd whatsapp-message-scheduler
```

### Run the Script

```bash
python send_whatsapp.py
```

### Follow the Prompts

- Enter recipient name  
- Enter recipient WhatsApp number  
- Enter message content  
- Enter scheduled date  
- Enter scheduled time  

---

## 🧠 How the Code Works (Line-by-Line Explanation)

### Step 1: Import Required Libraries

```python
from twilio.rest import Client
from datetime import datetime, timedelta
import time
```

- `Client` – Twilio SDK client  
- `datetime` – Date and time handling  
- `time` – Execution delay  

---

### Step 2: Define Twilio Credentials

```python
account_sid = '#############################'
auth_token = '################################'
from_number = '+14155238886'
```

---

### Step 3: Initialize Twilio Client

```python
client = Client(account_sid, auth_token)
```

---

### Step 4: Define WhatsApp Message Function

```python
def send_whatsapp_message(recipient_number, message_body):
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=message_body,
        to=f'whatsapp:{recipient_number}'
    )
```

---

### Step 5: Collect User Input

```python
name = input("Enter the recipient's name: ")
recipient_number = input("Enter the recipient's WhatsApp number: ")
message_body = input(f"Enter the message to send to {name}: ")
```

---

### Step 6: Collect Scheduled Date and Time

```python
date_str = input("Enter the date to send the message (DD-MM-YYYY): ")
time_str = input("Enter the time to send the message (HH:MM): ")
```

---

### Step 7: Convert to datetime Object

```python
scheduled_datetime = datetime.strptime(
    f"{date_str} {time_str}", "%d-%m-%Y %H:%M"
)
```

---

### Step 8: Calculate Delay

```python
current_datetime = datetime.now()
time_difference = scheduled_datetime - current_datetime
delay_seconds = time_difference.total_seconds()
```

---

### Step 9: Validate Scheduled Time

```python
if delay_seconds <= 0:
    print("The scheduled time is in the past.")
```

---

### Step 10: Wait and Send Message

```python
time.sleep(delay_seconds)
send_whatsapp_message(recipient_number, message_body)
```

---

## ⚠️ Limitations

- ❌ Cannot send messages to WhatsApp groups  
- ❌ Script must remain running until message is sent  
- ❌ Not suitable for large-scale production  

---

## 🔮 Possible Enhancements

- Use `cron` or `APScheduler`
- CSV-based recipients
- Logging support
- Environment variables
- Retry logic
- Docker support


---

## 🤝 Contributing

Pull requests are welcome.  
Please open an issue for major changes.
