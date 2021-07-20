import os
import logging
from slack_bolt import App
from slack_sdk import WebClient
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
    reqs = aptible_bot.show_queue_info()
    queue = slack_messages.create_queue(reqs)
    for i in range(0, len(queue)):
        try:
            result = app.client.chat_postMessage(
                channel=channel_id,
                blocks=queue[i],
                text="you should only see this if something went wrong, which means something went wrong. Please contact @vivienne!"
            )
            logger.info(result)
            # aptible_bot.status_update(reqs[i]['id'], 'filler')
        except SlackApiError as e:
            print(f"Error: {e}")


@app.action("approve")
def handle_approval(ack, body, client, say):
    ack()
    payload = body['message']['blocks']
    selections = body['state']['values']
    addtl_perms = aptible_bot.get_selections(payload, selections)
    if addtl_perms == 'yikes':
        say("Something went wrong with the permissions. Please contact @vivienne.")
    # get_email = client.users_info(user=body['user']['id'])
    # user_email = get_email['user']['profile']['email']
    user_email = 'vpustell@pagerduty.com'
    request_id = body['actions'][0]['value']
    approve_it = aptible_bot.approve_requests(request_id, user_email, addtl_perms)
    if approve_it == 'yay':
        say("Approval success!")
        update_request_screen(body['container'], client)
    else:
        print(approve_it)
        try:
            response = app.client.chat_postMessage(
                channel=channel_id,
                ts=body['container']['message_ts'],
                text=approve_it
            )
        except SlackApiError as e:
            print(f"Error: {e}")


@app.action("reject")
def handle_rejection(ack, body, client):
    ack()
    print('reject button go clicky')
    get_email = client.users_info(user=body['user']['id'])
    user_email = get_email['user']['profile']['email']


@app.action("perms")
def handle_perm_ticks(ack):
    ack()
    print('they messin with them boxes again')


def update_request_screen(msg_info, client):
    ts = msg_info['message_ts']
    try:
        result = app.client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=[{"type": "section", "text": {"type": "plain_text", "text": "hahahaha maniacal laughter"}}],
            text="You have successfully approved this request."
        )
    except SlackApiError as e:
        print(f"Error: {e}")


# start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
