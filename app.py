import os
import logging
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
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


# check the queue for new requests
queue_info = aptible_bot.pending_request_check()

# post new requests to slack
if queue_info != []:
    reqs = aptible_bot.get_queue_info(queue_info)
    queue = slack_messages.create_queue(reqs)
    for i in range(0, len(queue)):
        try:
            result = app.client.chat_postMessage(
                channel=channel_id,
                blocks=queue[i],
                text="you should only see this if something went wrong, which means something went wrong. Please contact @vivienne!"
            )
            logger.info(result)
        except SlackApiError as e:
            print(f"Error: {e}")


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
    # get_email = client.users_info(user=body['user']['id'])
    # user_email = get_email['user']['profile']['email']
    user_email = 'vpustell@pagerduty.com'
    request_id = body['actions'][0]['value']
    approve_it = aptible_bot.approve_requests(request_id, user_email, addtl_perms)
    if approve_it == 'yay':
        say("Approval success!")
        update_request_screen(body['container'], requester, user_email, 'approve', client)
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
    # process slack reject - update message, db, and aptible

    ack()
    print('reject button go clicky')
    get_email = client.users_info(user=body['user']['id'])
    user_email = get_email['user']['profile']['email']
    requester = body['message']['blocks'][1]['text']['text'][6:]
    get_feedback(body, client)
    # call a dialog to get the reason for the rejection and store it
    # use the aptible bot function for the db
    update_request_screen(body['container']['message_ts'], requester, user_email, 'reject', note, client)


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
    
    ack()
    note  = view['state']['values']['feedback_text']['feedback_input']
    user = body['user']
    requester = view['private_metadata']['requester']
    ts = view['private_metadata']['ts']
    update_request_screen(ts, requester, user, 'reject', note, client)


def get_feedback(body, origin_ts, requester, client):
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
            "private_metadata": {'ts': origin_ts, 'requester': requester}
        }
    )


def update_request_screen(ts, requester, user, status, note="N/A", client):
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


# setting up flask to provide safer happier friendly friend life
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
# FLASK_APP=app.py FLASK_ENV=development flask run -p 3000
