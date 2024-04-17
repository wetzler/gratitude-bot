import os
from twilio.rest import Client
import storage

# this stuff needs to be there for this to run on PythonAnywhere
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/.')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# Twilio credentials
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
client = Client(account_sid, auth_token)

def send_message(message_body,to_number,message_type):
    message = client.messages.create(
        body=message_body,
        from_=twilio_number,
        to=to_number
    )
    print(f"Message sent: {message.sid}")
    storage.store_message(twilio_number, to_number, message_body,message_type,message.sid)