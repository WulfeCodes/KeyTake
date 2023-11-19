from flask import Flask, jsonify, redirect, render_template, request, url_for
import requests
import json

from api_call import getMessages, GM_API_KEY

app = Flask(__name__)


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

@app.route("/fetch_group_data")
def fetch_group_data():
    group_data = fetchGroupData(access_token=GM_API_KEY)
    return group_data

# -------------------------------------------------------------------

# fetching the group_messages
# def getMessages(group_id):

#     data = fetchGroupData(access_token=GM_API_KEY) # a dictionary

#     for item in data['response']:
#         if item['id'] == group_id:            
#             return item['messages']
        

# @app.route("/get_messages")
# def get_messsages():
#     group_id = getMessages('95435321')
#     return group_id

# -------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

#------------------------------------------------------------------------
@app.route("/home")
def home():
    group_id = fetch_group_data()['response'] # it's  a dictionary.
    return render_template('home.html', group_id=group_id)

@app.route("/display_info")
def displayInfo():
    messages = getMessages(GM_API_KEY, '95435321')
    return messages


if __name__ == "__main__":
    app.run(debug=True)