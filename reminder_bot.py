import os
from twilio.rest import Client
import schedule
import time
import datetime
import storage

# this stuff needs to be there for this to run on PythonAnywhere
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
    storage.store_message(twilio_number, user_number, text_reminder,"scheduled_prompt",message.sid)

send_reminder()

# Schedule the reminder
schedule.every(2).hours.do(send_reminder)

# Keep the script running
while True:
    schedule.run_pending()
    print("Current time:", datetime.datetime.now())
    time.sleep(60)  # Check every minute