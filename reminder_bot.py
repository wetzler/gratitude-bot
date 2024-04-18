import os
from twilio.rest import Client
import schedule
import time
import datetime
import storage
import requests

# this stuff needs to be there for this to run on PythonAnywhere
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/.') 
load_dotenv(os.path.join(project_folder, '.env'))

# Twilio credentials
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')

# Airtable credentials
base_key = os.environ.get('AIRTABLE_BASE_KEY')
table_name = os.environ.get('AIRTABLE_TABLE_NAME')
access_token = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')

print(base_key)
# Get list of numbers that need reminders
url = f"https://api.airtable.com/v0/{base_key}/Users"  # Define the URL to make the request to the database

headers = {   # Define the headers for the request
    "Authorization": f"Bearer {access_token}"
}

# Make the GET request for the users data
response = requests.get(url, headers=headers)
data = response.json()
users = data.get('records', [])

# Get all user_number values
user_numbers = set(user['fields']['user_number'] for user in users)
print("Found "+str(len(user_numbers))+" users.")
print(user_numbers)

# Initialize Twilio client
client = Client(account_sid, auth_token)

def send_reminder(user_number):
    text_reminder = "hi, it's gratitude bot. what are you feeling grateful for today? 🌟"
    message = client.messages.create(
        body= text_reminder,
        from_=twilio_number,
        to=user_number
    )
    print(f"Message sent: {message.sid}")
    storage.store_message(twilio_number, user_number, text_reminder,"scheduled_prompt",message.sid)

# Call send_reminder for each user_number
for user_number in user_numbers:
    send_reminder(user_number)

# Schedule the reminder
schedule.every(2).hours.do(send_reminder)

# Keep the script running
while True:
    schedule.run_pending()
    print("Current time:", datetime.datetime.now())
    time.sleep(60)  # Check every minute