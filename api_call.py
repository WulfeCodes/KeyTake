from datetime import datetime, timedelta
# from app import fetchGroupData
import requests


# constants
GM_API_KEY = 'mlYGolL23Ch5uEEhTchiumiNGR15JqSWWiGyCwni'


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
    
    message_return = []
    for message in all_messages:
        message_raw = message['text']
        message_clean = message_raw.replace('\n', ' ')
        cleaned_message = ' '.join(message_clean.split())
        message_return.append({message['name']: cleaned_message})
    return message_return # returns a list of {name: message} | pass it to oneai




