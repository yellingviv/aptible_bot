import os
import logging
import time
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request
from dotenv import load_dotenv
import aptible_bot
import aptible_monitor
import slack_messages
import rooms_model

load_dotenv()

# initialize app with slack bot token and signing secret
app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)
logger = logging.getLogger(__name__)
channel_id = os.getenv('SLACK_CHANNEL_ID')

# setting up flask to provide safer happier friendly friend life
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# instantiate and connect to db
rooms_model.connect_to_db(flask_app)

# check the queue for new requests
queue_info = aptible_bot.pending_request_check()
print("queue size: ", len(queue_info))

@app.action("approve")
def handle_approval(ack, body, client, say):
    # approve via slack - update message in channel, update db, update aptible

    ack()
    requester = body['message']['blocks'][1]['text']['text'][6:]
    payload = body['message']['blocks']
    selections = body['state']['values']
    addtl_perms = aptible_bot.get_selections(payload, selections)
    if addtl_perms == 'yikes':
        say("Something went wrong with the permissions. Please contact @vivienne.")
    user_id = body['user']['id']
    # get_email = client.users_info(user=body['user']['id'])
    # user_email = get_email['user']['profile']['email']
    user_email = 'vpustell@pagerduty.com'
    request_id = body['actions'][0]['value']
    approve_it = aptible_bot.approve_requests(request_id, user_email, addtl_perms)
    if approve_it == 'yay':
        say("Approval success!")
        update_request_screen(body['container']['ts'], requester, user_id, 'approve', client)
        # call_some_db_update_here_please()
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
    # process slack reject - call for modal to get more info

    ack()
    print('reject button go clicky')
    user_id = body['user']['id']
    get_email = client.users_info(user=body['user']['id'])
    user_email = get_email['user']['profile']['email']
    requester = body['message']['blocks'][1]['text']['text'][6:]
    get_feedback(body['container']['ts'], requester, user_id, client)


@app.action("perms")
def handle_perm_ticks(ack):
    # honestly currently this does nothing but don't want errors!
    # this could be used to track selections, but i just pull from the final payload
    # this is purely to prevent error messages within the slack app that scare people

    ack()
    print('they messin with them boxes again')


@app.view("feedback")
def handle_view_submission(ack, body, client, view, logger):
    # process the submitted modal with rejection notes

    respond_close = {"response_action": "clear"}
    ack(respond_close)
    note  = view['state']['values']['feedback_text']['feedback_input']
    user_id = view['private_metadata']['user_id']
    requester = view['private_metadata']['requester']
    ts = view['private_metadata']['ts']
    update_request_screen(ts, requester, user_id, 'reject', client, note)
    # also call to update the db plz


def get_feedback(origin_ts, requester, user_id, client):
    # get feedback from reviewer on why the rejection via modal

    client.views_open(
        trigger_id=body['trigger_id'],
        view={
            "type": "modal",
            "callback_id": "feedback",
            "title": {"type": "plain_text", "text": "Review Details"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {"type": "input",
                "block_id": "feedback_text",
                "label": {"type": "plain_text", "text": "Please explain the reason for rejecting this request."},
                "element": {"type": "plain_text_input", "action_id": "feedback_input", "multiline": True},
                "optional": false
                }
            ],
            "notify_on_close": True,
            "private_metadata": {'ts': origin_ts, 'requester': requester, 'user_id': user_id}
        }
    )


def update_request_screen(ts, requester, user_id, status, client, note="N/A"):
    # update the original request message with new content on action from reviewer
    # used by the handle_rejection and handle_approval actions

    try:
        result = app.client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=[{"type": "section", "text": {"type": "plain_text", "text": "hahahaha maniacal laughter"}}],
            # blocks=slack_message.update_request(requester, user, status, note)
            text="You have successfully approved this request."
        )
    except SlackApiError as e:
        print(f"Error: {e}")


def monitor_the_queue():
    # post new requests to slack

    print("we are monitoring the queue")
    while True:
        if queue_info != []:
            print("we are inside the if loop for the queue check")
            reqs = aptible_bot.get_queue_info(queue_info)
            queue = slack_messages.create_queue(reqs)
            print("the queue")
            for i in range(0, len(queue)):
                print("block to send")
                try:
                    result = app.client.chat_postMessage(
                        channel=channel_id,
                        blocks=queue[i],
                        text="you should only see this if something went wrong, which means something went wrong. Please contact @vivienne!"
                    )
                    logger.info(result)
                except SlackApiError as e:
                    print(f"Error: {e}")

        # wait a minute then check again
        time.sleep(60)

monitor_the_queue()

# start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
