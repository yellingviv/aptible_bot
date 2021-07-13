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


queue_info = aptible_bot.pending_request_check()

if queue_info != []:
    for i in range(0, len(slack_messages.queue_blocks)):
        try:
            result = app.client.chat_postMessage(
                channel=channel_id,
                blocks=slack_messages.queue_blocks[i],
                text="in case of emergency, break glass"
            )
            logger.info(result)
        except SlackApiError as e:
            print(f"Error: {e}")


@app.action("approve")
def handle_approval(ack, body, respond):
    ack()
    print('approve button go clicky')
    respond(f"<@{['selected_user']}> made the approve button go clicky")


@app.action("reject")
def handle_rejection(ack, body, logger):
    ack()
    print('reject button go clicky')


@app.action("perms")
def handle_perm_ticks(ack, body, client):
    ack()
    get_email = client.users_info(user=body['user']['id'])
    user_email = get_email['user']['profile']['email']
    print(user_email)

# start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
