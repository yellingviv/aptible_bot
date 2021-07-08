import os
import logging
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import aptible_bot
import aptible_monitor
import slack_messages

load_dotenv()

# initialize app with slack bot token and signing secret
app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)
logger = logging.getLogger(__name__)
channel_id = os.getenv('SLACK_CHANNEL_ID')

# Add functionality here

def post_to_channel():
    # post a message to a channel yay

    print('trying to post to channel')

    try:
        # Call the conversations.list method using the WebClient
        result = app.client.chat_postMessage(
            channel=channel_id,
            #blocks=new_request,
            text='henlo???'
        )
        # Print result, which includes information about the message (like TS)
        print(result)

    except SlackApiError as e:
        print(f'Error: {e}')


# start the app
if __name__ == '__main__':
    app.start(port=int(os.environ.get('PORT', 3000)))
