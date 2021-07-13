import os
import logging
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from flask import Flask, request
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

try:
    result = app.client.chat_postMessage(
        channel=channel_id,
        blocks=slack_messages.new_request,
        text="in case of emergency, break glass"
    )
    logger.info(result)

except SlackApiError as e:
    print(f"Error: {e}")


@app.action("button_click")
def update_permissions(ack, body, payload):
    ack()
    print('did i succed')
    print(payload)
    say("I clicked it")


# start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
