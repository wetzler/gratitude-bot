import os
from twilio.rest import Client
import schedule
import time
import datetime
import storage
import requests
import pytz
from datetime import datetime
import generative_ai
import logging

# Set up logging
logging.basicConfig(filename='reminder_bot.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

logging.info('Reminderbot script started')

# And logging.error() to log errors
try:

    # load env variables 
    logging.info('Loading env variables')
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # Twilio credentials
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')

    logging.info("regular reminders sending from: "+twilio_number)
    print("regular reminders sending from: "+twilio_number)

    # Airtable credentials
    base_key = os.environ.get('AIRTABLE_BASE_KEY')
    table_name = os.environ.get('AIRTABLE_TABLE_NAME')
    access_token = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')

    def get_latest_users():
        # Get list of numbers that need reminders
        logging.info("Getting list of users from airtable.")
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
        logging.info("Found "+str(len(user_numbers))+" users.")
        logging.info(user_numbers)
        return user_numbers

    # Initialize Twilio client
    logging.info("Initializing Twilio client.")
    client = Client(account_sid, auth_token)

    def send_reminder(user_numbers):
        logging.info("Sending reminders")
        for user_number in user_numbers:
            #text_reminder = "hi, it's gratitude bot. what are you feeling grateful for today? 🌟"
            text_reminder = generative_ai.generate_daily_prompt()
            message = client.messages.create(
                body= text_reminder,
                from_=twilio_number,
                to=user_number
            )
            print(f"Message sent: {message.sid}")
            storage.store_message(twilio_number, user_number, text_reminder,"scheduled_prompt",message.sid)

    def send_reminders_to_latest_users():
        user_numbers = get_latest_users()
        send_reminder(user_numbers)

    # Call the function once immediately
    send_reminders_to_latest_users()

    # Schedule the reminder
    job = schedule.every(24).hours.do(send_reminders_to_latest_users)

    # Keep the script running and post logs so we can see that it's up and when the next run is
    while True:
        schedule.run_pending()
        
        current_time_pst = datetime.now(pytz.timezone('US/Pacific'))     # Get current time in PST
        next_run_local = job.next_run
        next_run_pst = next_run_local.astimezone(pytz.timezone('US/Pacific'))

        print("Current time (PST):", current_time_pst.strftime('%m-%d %H:%M'), "0=0=0=0=0=0=0=0=0=0 Next run at (PST):", next_run_pst.strftime('%m-%d %H:%M'))

        time.sleep(300)  # Check every 5 minutes

except Exception as e:
    logging.error('Failed to do something: ' + str(e))