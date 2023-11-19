from openai import OpenAI
import os
from dotenv import load_dotenv
import requests

load_dotenv()  # This loads the environment variables from `.env`.

# Now you can use os.environ to get environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FLASK_SERVER_URL = 'http://localhost:5000/get_messages'  # URL of the Flask server

# response = requests.get(FLASK_SERVER_URL)

# Make a request to the Flask server to get messages
response = requests.get(FLASK_SERVER_URL)
if response.status_code == 200:
    messages = response.json()  # Assuming response is JSON-formatted
    # Extract the text from the first message or however you prefer
    user_content = messages[0]['text'] if messages else "No messages found."

    # Setup OpenAI client and make the completion request
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a summarization bot, skilled in summarizing text messages."},
            {"role": "user", "content": f"Summarize these messages and output them as bullet points: {user_content}"}
        ]
    )

    print(completion.choices[0].message)
else:
    print("Failed to fetch messages from Flask server.")


# client = OpenAI()

# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )

# print(completion.choices[0].message)
