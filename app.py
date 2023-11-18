from flask import Flask, jsonify, render_template
import requests
import json

app = Flask(__name__)

# constants
GM_API_KEY = 'mlYGolL23Ch5uEEhTchiumiNGR15JqSWWiGyCwni'

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
def getMessages(group_id):

    data = fetchGroupData(access_token=GM_API_KEY) # a dictionary

    for item in data['response']:
        if item['id'] == group_id:            
            return item['messages']
        

@app.route("/get_messages")
def get_messsages():
    group_id = getMessages('95435321')
    return group_id

# -------------------------------------------------------------------

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/home")
def home():
    group_id = fetch_group_id()['response'] # it's  a dictionary.
    return render_template('home.html', group_id=group_id)


@app.route("/login")
def login():
    return "<h1>login page</h1>"



if __name__ == "__main__":
    app.run(debug=True)