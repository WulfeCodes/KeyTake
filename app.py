from flask import Flask, jsonify, render_template
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv



app = Flask(__name__)

load_dotenv()  # This loads the environment variables from `.env`.

# Now you can use os.environ to get environment variables
GM_API_KEY = os.getenv('GM_API_KEY')

# fetching the group_ids
def fetchGroupData(access_token):
    url = 'https://api.groupme.com/v3/groups'
    headers = {
        'Content-Type': 'application/json',
        'X-Access-Token': access_token,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get groups. Status code: {response.status_code}")
        return None

@app.route("/fetch_group_id")
def fetch_group_data():
    group_id = fetchGroupData(access_token=GM_API_KEY)
    return group_id

# -------------------------------------------------------------------

# fetching the group_messages
def getMessages(access_token, group_id):
    # Define the base URL for the GroupMe API
    base_url = f"https://api.groupme.com/v3/groups/{group_id}/messages"
    
    # Calculate the timestamp for one week ago
    one_week_ago = datetime.now() - timedelta(weeks=1)
    
    # Initialize parameters for the API call
    params = {
        'token': access_token,
        'limit': 100  # Set limit to the maximum value
    }

    all_messages = []
    fetch_more = True

    while fetch_more:
        # Make the API call
        response = requests.get(base_url, params=params)
        
        # Check the response status
        if response.status_code == 200:
            data = response.json()['response']
            messages = data['messages']
            print(type(messages))

            # Check if the last message is older than one week
            if messages:
                # Convert the 'created_at' timestamp to a datetime object
                last_message_time = datetime.utcfromtimestamp(messages[-1]['created_at'])
                
                # If the last message is within the past week, fetch the next batch
                fetch_more = last_message_time > one_week_ago
                
                # Update the before_id to fetch the next batch of messages
                params['before_id'] = messages[-1]['id']
                
                # Extract only relevant information and add to the list
                for message in messages:
                    message_time = datetime.utcfromtimestamp(message['created_at'])
                    # Check if the message is within the past week
                    if message_time > one_week_ago:
                        all_messages.append({
                            'id': message['id'],
                            'name': message['name'],
                            'text': message['text'],
                            'created_at': datetime.utcfromtimestamp(message['created_at'])
                        })
                    else:
                        # If a message is older than one week, stop fetching
                        fetch_more = False
                        break
        elif response.status_code == 304:
            # No more messages found
            break
        else:
            # Handle other errors (e.g., network or authorization issues)
            print("Error:", response.status_code, response.text)
            fetch_more = False
    
    return all_messages
        

@app.route("/get_messages")
def get_messages():
    messages = getMessages(GM_API_KEY, '95435321')
    # return messages
    return jsonify(messages)

# -------------------------------------------------------------------

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/home")
def home():
    group_id = fetch_group_data()['response'] # it's  a dictionary.
    return render_template('home.html', group_id=group_id)


@app.route("/login")
def login():
    return "<h1>login page</h1>"



if __name__ == "__main__":
    app.run(debug=True)