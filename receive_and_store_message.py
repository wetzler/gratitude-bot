import os
import requests
import urllib.parse
from flask import Flask, request
import storage
import generative_ai
import send_response
from datetime import datetime

# load env variables 
from dotenv import load_dotenv
load_dotenv(override=True)

# Get Airtable parameters from environment variables
base_key = os.environ.get('AIRTABLE_BASE_KEY')
table_name = os.environ.get('AIRTABLE_TABLE_NAME')
access_token = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')

# Get Gratitidue Bot's Number
twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')

app = Flask(__name__)

@app.route('/sms', methods=['POST'])  # Create a route for when a message come in from Twilio
def sms():
    # Get the text message details
    from_number = request.form['From']
    to_number = request.form['To']
    message_body = request.form['Body']
    twilio_message_sid  = request.form['MessageSid']
    print("New incoming message from "+ from_number + ": "+ message_body)

    # Log the message
    storage_response = storage.store_message(from_number, to_number, message_body,"incoming user message",twilio_message_sid)
    print("Storing the message in Airtable.")
    # print(storage_response)

    # Get the full user conversation history
    # Define the filter formula to find messages to or from this number
    filter_formula = f"(OR(from_number='{from_number}', to_number='{from_number}'))"

    # URL-encode the filter formula so that we can make the request
    filter_formula = urllib.parse.quote(filter_formula)

    # Define the URL to make the request to the database
    url = f"https://api.airtable.com/v0/{base_key}/{table_name}?filterByFormula={filter_formula}"
    headers = {"Authorization": f"Bearer {access_token}"} # Define the headers for the request

    #recentmessages = requests.get(url, headers=headers)
    
    conversation_history = []
    offset = None  # used to handle pagination of the results from the Airtable API
    print("Getting conversation history from Airtable.")

    while True:
        if offset:
            paginated_url = url + f"&offset={offset}"
            print("Getting more conversation history from Airtable. Offset: " + str(offset))
        else:
            paginated_url = url

        response = requests.get(paginated_url, headers=headers) # Make the GET request for the conversation data
        response_json = response.json()

        records = response_json.get('records', [])
        conversation_history.extend(records)

        offset = response_json.get('offset')
        if not offset:
            break    
    
    print("Found "+str(len(conversation_history))+" messages in this conversation.")
    
    # sort the messages by created time starting with the oldest
    conversation_history.sort(key=lambda x: x['fields']['created_time'], reverse=False) 

    # reformat the conversation to be easily readable in logs and by generative AI
    print("Reformatting conversation history for readability.")
    formatted_records = []
    for message in conversation_history:
        timestamp = datetime.strptime(message['createdTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
        conversation_from_number = message['fields']['from_number']
        if conversation_from_number == twilio_number:
            conversation_from_number = "gratitude bot"
        elif conversation_from_number == from_number:
            conversation_from_number = "subscriber"
        message_content = message['fields'].get('message_body', 'system note: no message (might have been a photo or something else)')
        formatted_record = f"[{timestamp}] {conversation_from_number}: \"{message_content}\""
        formatted_records.append(formatted_record)
    conversation_history = "\n".join(formatted_records)
    print(conversation_history)

    print("Figuring out what to do based on the latest message")
    user_number = from_number
    # check if the incoming message is from a new subscriber
    if message_body in ["START", "start", "Start", "Restart", "restart", "RESTART"]:
        # send a welcome message
        welcome_message = "hi! my name is gratitude bot! i send daily gratitude prompts. you can reply STOP at anytime. what are you grateful for today? 🌟"
        print("Sending a welcome message to a new user: " + welcome_message) 
        send_response.send_message(welcome_message, user_number, "new_user_subscribed_welcome_message")
        storage.store_user(user_number, message_body)
    elif not conversation_history:
        # send a welcome message
        welcome_message = "hi! my name is gratitude bot! i send daily gratitude prompts. reply START to subscribe. you can reply STOP at anytime. what are you grateful for today? 🌟"
        print("Sending a welcome message to a new user: " + welcome_message) 
        send_response.send_message(welcome_message, user_number, "new_user_start_to_subscribe_welcome_message")
        storage.store_user(user_number, message_body)
    elif message_body in ["STOP", "stop", "Stop"]:
        goodbye_message = "i'll stop sending messages now! send START to subscribe again. have a great day! 🌟"
        print("Sending a goodbye message to a user who has unsubscribed: " + goodbye_message)
        send_response.send_message(goodbye_message, user_number, "unsubscribe_message")
        storage.remove_user(user_number)
    else:  #Ask AI to generate a followup reponse
        print("Crafting a followup response!")
        followup_question = generative_ai.generate_responsev2(conversation_history)
        print("Sending our followup response: " + followup_question.content)
        send_response.send_message(followup_question.content, user_number, "gb_response")
    return "Message received"

if __name__ == '__main__':
    app.run(debug=True, port=8000)  # use this for local development
    # app.run()  # use this for PythonAnywhere
