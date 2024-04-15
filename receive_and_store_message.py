import os
import json
import datetime
import requests
import urllib.parse
from flask import Flask, request
from openai import OpenAI
from datetime import datetime, timedelta
import storage
import generative_ai
import send_response

# Get Airtable parameters from environment variables
base_key = os.getenv('AIRTABLE_BASE_KEY')
table_name = os.getenv('AIRTABLE_TABLE_NAME')
access_token = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')

app = Flask(__name__) 

@app.route('/sms', methods=['POST'])
def sms():
    # Get the text message details
    from_number = request.form['From']
    to_number = request.form['To']
    message_body = request.form['Body']
    twilio_message_sid  = request.form['MessageSid']
    print("New message from "+ from_number + ": "+ message_body)

    # Log the message
    storage.store_message(from_number, to_number, message_body,"incoming user message",twilio_message_sid)

    # Get some information about this conversation so we can figure out what to do next 
    # Define the filter formula to find messages to or from this number 
    filter_formula = f"(OR(from_number='{from_number}', to_number='{from_number}'))"   
    # to-do: only get the messages from the last 24 hours instead of all of them

    # URL-encode the filter formula
    filter_formula = urllib.parse.quote(filter_formula)

    # Define the URL to make the request to the database
    url = f"https://api.airtable.com/v0/{base_key}/{table_name}?filterByFormula={filter_formula}"

    # Define the headers for the request 
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Make the GET request for the conversation data 
    recentmessages = requests.get(url, headers=headers)
    # Parse the JSON response
    data = recentmessages.json()
    records = data.get('records', [])
    print("Found "+str(len(records))+" records in this conversation.")

    # Sort the records by created time so the most recent is first
    records.sort(key=lambda x: x['fields']['created_time'], reverse=True)
    # Exclude the current incoming message from our list of previous messages
    records = [record for record in records if 'twilio_message_sid' in record['fields'] and record['fields']['twilio_message_sid'] != twilio_message_sid]
    # Get the most recent message prior to this one so we can figure out what to do next
    previous_message = records[0]['fields']['message_body']
    print("The previous message was: "+previous_message)

    # check if the previous message contains "gratitude bot". If so, assume this text is a response to our daily prompt and ask a followup question
    if "gratitude bot" in previous_message:
        #ask AI to genereate a followup question
        followup_question = generative_ai.generate_response(message_body)
        print("Our followup question: "+followup_question.content)  
        user_number=from_number
        send_response.send_message(followup_question.content,user_number,"followup_question")  
    return "Message received"

if __name__ == '__main__':
    app.run(debug=True, port=8000)