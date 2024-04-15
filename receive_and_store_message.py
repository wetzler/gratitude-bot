import os
import json
import requests
import urllib.parse
from flask import Flask, request
from openai import OpenAI
from datetime import datetime, timedelta
import storage

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

    # store the message
    storage.store_message(from_number, to_number, message_body, message_type='incoming')

    # Check if it's a response to our initial question or a followup question
    # Is the most recent message in the conversation our daily prompt? If so, send a followup question.
    # If we haven't received a message from that number in the last 12hr, we assume it's an answer to our daily prompt.
    # Check airtable for a message from that number in the last 24hr.
    # Get the time 12 hours ago
    time_12_hours_ago = (datetime.now() - timedelta(hours=12)).isoformat()

    # Define the filter formula
    filter_formula = "AND({{from_number}} = '{}', {{created_time}} > '{}')".format(number, time_12_hours_ago)

    # URL-encode the filter formula
    filter_formula = urllib.parse.quote(filter_formula)

    # Define the URL to send the message details to
    url = f"https://api.airtable.com/v0/{base_key}/{table_name}?filterByFormula={filter_formula}"

    # Define the headers for the request 
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Make the GET request
    recentmessages = requests.get(url, headers=headers)

    # Parse the JSON response
    data = recentmessages.json()
    records = data.get('records', [])

    # in case the latest message has already been written, remove it from the records
    # delete any record whose UserResponse is the same as the message_body
    records = [obj for obj in records if obj['fields']['message_body'] != message_body]

    # If we have a record, it's a followup question
    # If the length of records is greater than 0, we have a record
    if len(records) == 0:
        print ("the records length was 0")
        print ("we'll ask for more detail now")
        from openai import OpenAI
        client = OpenAI()
        completion = client.chat.completions.create( 
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a conversational assistant that helps people express and share gratitude. You are friendly, calm, and supportive."},
            {"role": "user", "content": "Someone has recently logged the following in their gratitude journal. In under 160 characters, ask them a followup question related to the entry in order to add impact and vibrancy to the memory. \
            Entry: I'm grateful for my friend Alissa"}
        ]
        )
        print(completion.choices[0].message)
    else:    
        print ("the records length was > 0")
        print (len(records))
        print ("we already got enough responses today!")
    return '', 200

if __name__ == '__main__':
    app.run(debug=True, port=8000)