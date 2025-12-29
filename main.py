# Step 1: Import necessary libraries

from twilio.rest import Client
from datetime import datetime, timedelta
import time

# Step 2: Define Twilio credentials

account_sid = '#############################'
auth_token = '################################'
from_number = '+14155238886'

client = Client(account_sid, auth_token)


# Step 3: Define function to send SMS

def send_whatsapp_message(recipient_number, message_body):
    try:
        message = client.messages.create(
            from_= 'whatsapp:+14155238886',
            body = message_body,
            to= f'whatsapp:{recipient_number}'
        )
        print(f"Message sent to {recipient_number} seccessfully. SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send message to {recipient_number}. Error: {str(e)}")


# Step 4: User input for recipient name and number 

name = input("Enter the recipient's name: ")
recipient_number = input("Enter the recipient's WhatsApp number (with country code, e.g., +1234567890): ")  
message_body = input(f'enter the message to send to {name}: ')

# Step 5 : parse date/time and calculate delay

date_str = input('Enter the date to send the message (DD-MM-YYYY): ')
time_str = input('Enter the time to send the message (HH:MM in 24-hour format): ')

#datetime object for scheduled time
scheduled_datetime = datetime.strptime(f'{date_str} {time_str}', '%d-%m-%Y %H:%M')
current_datetime = datetime.now()

#calculate delay
time_difference = scheduled_datetime - current_datetime
delay_seconds = time_difference.total_seconds()

if delay_seconds <= 0:
    print("The scheduled time is in the past. Please enter a future date and time.")
else:
    print(f"Message scheduled to be sent to {name} at {scheduled_datetime}.")

    #wait until the scheduled time
    time.sleep(delay_seconds)
    #send the message
    send_whatsapp_message(recipient_number, message_body)


