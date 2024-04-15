import os
from twilio.rest import Client
import schedule
import time
import datetime
import storage 
from dotenv import load_dotenv

project_folder = os.path.expanduser('~/.')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# Twilio credentials
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
user_number = os.environ.get('PERSONAL_PHONE_NUMBER')

# Initialize Twilio client
client = Client(account_sid, auth_token)

def send_reminder():
    text_reminder = "hi, it's gratitude bot. what are you feeling grateful for today? 🌟"
    message = client.messages.create(
        body= text_reminder,
        from_=twilio_number,
        to=user_number
    )
    print(f"Message sent: {message.sid}")
    storage.store_message(twilio_number, user_number, text_reminder, message_type='scheduled_prompt')

# Schedule the reminder
schedule.every(5).minutes.do(send_reminder)

# Keep the script running
while True:
    schedule.run_pending()
    print("Current time:", datetime.datetime.now())
    time.sleep(60)  # Check every minute