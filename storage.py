import os
import json
import requests
import urllib.parse

# this stuff needs to be there for this to run on PythonAnywhere
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/.')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# Get Airtable parameters from environment variables
base_key = os.environ.get('AIRTABLE_BASE_KEY')
table_name = os.environ.get('AIRTABLE_TABLE_NAME')
access_token = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')

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

def store_user(user_number, first_message):
    # Define the URL to send the user details to
    url = f"https://api.airtable.com/v0/{base_key}/Users"

    # Define the headers and data for the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "fields": {
            "user_number": user_number,
            "first_message": first_message
        }
    }
    # Make the post request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def remove_user(user_number):
    # Define the filter formula to find the record_id for this user
    filter_formula = f"(user_number='{user_number}')"
    # URL-encode the filter formula
    filter_formula = urllib.parse.quote(filter_formula)
    # Define the URL to make the request to the database
    url = f"https://api.airtable.com/v0/{base_key}/Users?filterByFormula={filter_formula}"

    # Define the headers for the request
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Make the GET request for the data
    response = requests.get(url, headers=headers)
    record = response.json()
    record_id = record['id']

    # Define the URL to delete the record
    url = f"https://api.airtable.com/v0/{base_key}/users/{record_id}"

    # Define the headers and data for the request
    headers = { "Authorization": f"Bearer {access_token}" }

    # Make the delete request
    response = requests.delete(url, headers=headers)
    return response.status_code