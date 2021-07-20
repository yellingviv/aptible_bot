# a separate file for all the slack message block kit blocks
# this shit just gets long and i don't wanna crowd the main app file

import aptible_bot
from datetime import datetime

def create_queue(reqs):

    queue_blocks = []

    for i in range(0, len(reqs)):
        if reqs[i]['status'] == 'requested':
            req_block =[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":sparkles: Aptible Room Request :sparkles:"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<" + reqs[i]['url'] + "|New request> from " + reqs[i]['from']
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Requested received at: " + reqs[i]['time']
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Message: " + reqs[i]['message']
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "checkboxes",
                         "options": aptible_bot.get_perms(),
                        "action_id": "perms"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "All requests are granted standard permissions. Use the checkboxes to add additional permissions if needed."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Approve Request"
                            },
                            "value": reqs[i]['id'],
                            "action_id": "approve"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Reject Request"
                            },
                            "value": reqs[i]['id'],
                            "action_id": "reject"
                        }
                    ]
                }
            ]
            queue_blocks.append(req_block)
        else:
            print("Queue not included: ")
            print(reqs[i]['name'], reqs[i]['status'])

    return queue_blocks


def update_request_approved(from, user):

    approved_time = datetime.now()
    stamp = approved_time.strftime("%B %d, %Y, %I:%M %p")
    approved_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":sparkles: Aptible Room Request :sparkles:"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Request from " ugh + " approved by " + user + " at " + stamp
            }
        }]

    return approved_blocks
