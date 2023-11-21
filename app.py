from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.server_api import ServerApi


app = Flask(__name__)

load_dotenv()
GM_API_KEY = os.getenv('GM_API_KEY')
ONEAI_KEY = os.getenv('ONEAI_KEY')

# database configuration--------------------------------------------------------
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PW = os.getenv('MONGO_PW')
uri = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PW}@freecluster.xfcsiur.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['AIATL']
groups_collection = db['Groups']
messages_collection = db['Messages']
oneai_collection = db['OneAISummary']

# fetching the group_ids -------------------------------------------------------
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

def insert_groups_into_mongodb(groups, collection):
    for group in groups['response']:
        group_info = {'id': group['id'], 
                       'name': group['name'],
                       'image_url': group['image_url']}
        collection.update_one({'id': group['id']}, {'$set': group_info}, upsert=True)


def retrieve_groups_from_mongodb(collection):
    groups_cursor = collection.find({})
    return list(groups_cursor)


@app.route("/home")
def fetch_group_data():
    groups = fetchGroupData(access_token=GM_API_KEY)
    insert_groups_into_mongodb(groups, groups_collection)
    groups_from_db = retrieve_groups_from_mongodb(groups_collection)
    return render_template('home.html', group_data=groups_from_db)
# ------------------------------------------------------------------------------

# fetching the group_messages---------------------------------------------------
def getMessages(access_token, group_id):
    url = f"https://api.groupme.com/v3/groups/{group_id}/messages"
    
    # Change for different time periods
    one_week_ago = datetime.now() - timedelta(weeks=1)
    # one_day_ago = datetime.now() - timedelta(days=1)
    
    # Initialize parameters for the API call
    params = {
        'token': access_token,
        'limit': 100
    }

    all_messages = []
    fetch_more = True

    while fetch_more:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()['response']
            messages = data['messages']

            if messages:
                last_message_time = datetime.utcfromtimestamp(messages[-1]['created_at'])
                fetch_more = last_message_time > one_week_ago
                params['before_id'] = messages[-1]['id']
                
                for message in messages:
                    message_time = datetime.utcfromtimestamp(message['created_at'])
                    # if message_time > one_day_ago:
                    if message_time > one_week_ago:
                        message_info = {
                            'id': message['id'],
                            'group_id': message['group_id'],
                            'name': message['name'],
                            'text': message['text'],
                            'created_at': datetime.utcfromtimestamp(message['created_at'])
                        }
                        all_messages.append(message_info)
                    else:
                        fetch_more = False
                        break
        elif response.status_code == 304:
            print('No more messages found')
            break
        else:
            print("Error:", response.status_code, response.text)
            fetch_more = False
    
    return all_messages
        

def insert_messages_into_mongodb(messages, collection):
    for message in messages:
        collection.update_one({'id': message['id']}, {'$set': message}, upsert=True)


def retrieve_messages_from_mongodb(collection, filter):
    messages_cursor = collection.find({'group_id': f'{filter}'}) # Filter must be string
    return list(messages_cursor)


def getFormattedMessages(messages_from_db):
    formatted_messages = []
    for message in messages_from_db:
        try:
            speaker = message.get("name","")
        except KeyError:
            speaker = "Unknown"
        utterance = message.get("text", "")
        formatted_message = {"speaker": speaker, "utterance": utterance}
        formatted_messages.append(formatted_message)

    return formatted_messages


def oneAi_summary(oneAi_token, messages, skill): # message is in {name: message} form
    url = "https://api.oneai.com/api/v0/pipeline"
  
    headers = {
        "api-key": oneAi_token, 
        "content-type": "application/json"
    }
    payload = {
        "input": messages,
        "input_type": "conversation",
        "content_type": "application/json",
        "output_type": "json",
        "multilingual": {
            "enabled": True
        },
        "steps": [
            {
                "skill": skill
            }
        ],
    }
    r = requests.post(url, json=payload, headers=headers)
    data = r.json()
    try:
        r = requests.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        print(data)
        return data['output'][0]['contents'][0]['utterance']  # text
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {e}")
    except KeyError as e:
        print(f"Key error in parsing response: {e}")
    except IndexError as e:
        print(f"Index error in parsing response: {e}")
    return None


@app.route("/group/<int:group_id>")
def load_group_page(group_id):

    messages = getMessages(access_token=GM_API_KEY, group_id=group_id)
    insert_messages_into_mongodb(messages, messages_collection)
    messages_from_db = retrieve_messages_from_mongodb(messages_collection, group_id)
    formatted_messages = getFormattedMessages(messages_from_db)
    print(formatted_messages)
    print("A")
    summary = oneAi_summary(ONEAI_KEY, formatted_messages, "summarize")
    print(f'Summary: {summary}\n')
    # summary = "Avihhan has joined the group. Zach Cheng, Vijay Wulfekuhle and Raphael Palacio will go to Chick-fil-A on Saturday at 8 pm."
    print("B")
    # action_items = oneAi_summary(ONEAI_KEY, formatted_messages, "action-items")
    # print(f'Action Items: {action_items}\n')
    action_items = "Lunch at Chick-fil-A on Saturday at 8 pm."
    print("C")

    return render_template('group_page.html', summary=summary, action_items=action_items)
# -------------------------------------------------------------------


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
