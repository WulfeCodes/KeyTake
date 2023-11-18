

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.groupme
action_items_collection = db.action_items

# OneAI API call
def process_oneai(text):
    url = "https://api.oneai.com/api/v0/pipeline"
    headers = {
        'api-key': '', # OneAI API KEY Here
        'Content-Type': 'application/json'
    }
    payload = {
        "input": text,
        "steps": [
            {"skill": "action-items"},
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()  # Make sure to handle errors and status codes in production

def fetchGroupID():
    url = f"https://api.groupme.com/v3/groups"
    response = requests.get(url)
    if response.status_code == 200:
            data = response.json()
            groups = data['response']
            for group in groups:
                print(f"Group Name: {group['id']}, Group ID: {group['name']}")
    else:
        print(f"Error {response.status_code}: {response.text}")

# GroupMe API call
def fetch_groupme_messages(group_id):
    url = f"https://api.groupme.com/v3/groups/{group_id}/messages"
    params = {
        'token': 'YOUR_GROUPME_ACCESS_TOKEN',
        'limit': 100  
    }
    response = requests.get(url, params=params)
    messages = response.json().get('response', {}).get('messages', [])
    # Extract the text from the messages
    text = ' '.join([msg['text'] for msg in messages if msg['text'] is not None])
    return text



@app.route('/process_groupme_messages', methods=['POST'])
def process_groupme_messages():
    data = request.json
    group_id = data['group_id']
    print(group_id)

    # Fetch messages from GroupMe
    messages = fetch_groupme_messages(group_id)

    # Process messages through OneAI
    processed_data = process_oneai(messages)

    # Store in MongoDB
    action_items_collection.insert_many(processed_data)

    return jsonify({"status": "success", "data": processed_data})

# Additional routes can be added as needed

def main():
     fetchGroupID()

if __name__ == '__main__':
    # app.run(debug=True)
    # fetchGroupID()
    main()

@app.route("/")    
def home():
     return "<p> Test file </p>"

