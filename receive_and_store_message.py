import os
import requests
import urllib.parse
from flask import Flask, request
import storage
import generative_ai
import send_response

# this stuff needs to be there for this to run on PythonAnywhere
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/.')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# Get Airtable parameters from environment variables
base_key = os.environ.get('AIRTABLE_BASE_KEY')
table_name = os.environ.get('AIRTABLE_TABLE_NAME')
access_token = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/sms', methods=['POST'])
def sms():
    print(table_name)
    # Get the text message details
    from_number = request.form['From']
    to_number = request.form['To']
    message_body = request.form['Body']
    twilio_message_sid  = request.form['MessageSid']
    print("New message from "+ from_number + ": "+ message_body)

    # Log the message
    response = storage.store_message(from_number, to_number, message_body,"incoming user message",twilio_message_sid)
    print(response)
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
    data = recentmessages.json()
    records = data.get('records', [])
    print("Found "+str(len(records))+" records in this conversation.")

    # Sort the records by created time so the most recent is first
    records.sort(key=lambda x: x['fields']['created_time'], reverse=True)
    # Exclude the current incoming message from our list of previous messages
    records = [record for record in records if 'twilio_message_sid' in record['fields'] and record['fields']['twilio_message_sid'] != twilio_message_sid]
    # Get the most recent message prior to this one so we can figure out what to do next
    previous_message = records[0]['fields']['message_body']
    print("The previous message was: " + previous_message)

    user_number = from_number
    # check if it's a new subscriber
    if message_body in ["START", "start", "Start", "Restart", "restart", "RESTART"]:
        # send a welcome message
        welcome_message = "hi! my name is gratitude bot! i send daily gratitude prompts. you can reply STOP at anytime. what are you grateful for today? 🌟"
        send_response.send_message(welcome_message, user_number, "new_user_subscribed_welcome_message")
        storage.store_user(user_number, message_body)
    elif not records:
        # send a welcome message
        welcome_message = "hi! ny name is gratitude bot! i send daily gratitude prompts. reply START to subscribe. you can reply STOP at anytime. what are you grateful for today? 🌟"
        send_response.send_message(welcome_message, user_number, "new_user_start_to_subscribe_welcome_message")
        storage.store_user(user_number, message_body)
    elif message_body in ["STOP", "stop", "Stop"]:
        goodbye_message = "i'll stop sending messages now! send START to subscribe again. have a great day! 🌟"
        send_response.send_message(goodbye_message, user_number, "unsubscribe_message")
        storage.remove_user(user_number)
    # check if the previous message contains "gratitude bot". If so, assume this text is a response to prompts and ask a followup question
    elif "gratitude bot" in previous_message or "daily reminder" in previous_message:
        # ask AI to generate a followup question
        followup_question = generative_ai.generate_response(message_body)
        print("Our followup question: " + followup_question.content)
        send_response.send_message(followup_question.content, user_number, "followup_question")
    # else:
    #     #send a thank you message
    #     thank_you_message = "thanks for sharing. keep it up! 🌟"
    #     send_response.send_message(thank_you_message, user_number, "thanks_for_submitting")
    return "Message received"

if __name__ == '__main__':
    app.run(debug=True, port=8000)  # use this for local development
    # app.run()  # use this for PythonAnywhere
