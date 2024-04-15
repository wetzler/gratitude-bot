import os
import json
import requests

# Get Airtable parameters from environment variables
base_key = os.getenv('AIRTABLE_BASE_KEY')
table_name = os.getenv('AIRTABLE_TABLE_NAME')
access_token = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')

def store_message(from_number, to_number, message_body, message_type, twilio_message_sid):
   
    # Define the URL to send the message details to
    url = f"https://api.airtable.com/v0/{base_key}/{table_name}"

    # Define the headers and data for the request 
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "fields": {
            "from_number": from_number,
            "to_number": to_number,
            "message_body": message_body,
            "message_type": message_type,
            "twilio_message_sid": twilio_message_sid
        }
    }
    # Make the post request 
    response = requests.post(url, headers=headers, data=json.dumps(data))

    return response.json()