import os
import json
import requests
from flask import Flask, request
from airtable import Airtable

# Get Airtable parameters from environment variables
base_key = os.getenv('AIRTABLE_BASE_KEY')
table_name = os.getenv('AIRTABLE_TABLE_NAME')
access_token = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')

app = Flask(__name__) 

@app.route('/sms', methods=['POST'])
def sms():
    number = request.form['From']
    message_body = request.form['Body']

    # Insert a row of data
    airtable.insert({'Number': number, 'Message': message_body})

    # Define the URL
    url = f"https://api.airtable.com/v0/{base_key}/{table_name}"

    # Define the headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "fields": {
            "UserNumber": number,
            "UserResponse": message_body
        }
    }
    # Make the request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Print the response
    print(response.json())

    return '', 200

if __name__ == '__main__':
    app.run(debug=True)