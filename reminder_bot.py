import os
from twilio.rest import Client
import schedule
import time

# Twilio credentials
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
your_number = os.environ.get('PERSONAL_PHONE_NUMBER')

# Initialize Twilio client
client = Client(account_sid, auth_token)

def send_reminder():
    message = client.messages.create(
        body="hi, it's gratitude bot. what are you feeling grateful for today? 🌟",
        from_=twilio_number,
        to=your_number
    )
    print(f"Message sent: {message.sid}")

send_reminder()
# Schedule the reminder
schedule.every().day.at("10:00").do(send_reminder)

# Keep the script running
while True:
    schedule.run_pending()
    print("i'm running")
    time.sleep(60)  # Check every minute