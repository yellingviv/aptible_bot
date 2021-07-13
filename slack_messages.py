# a separate file for all the slack message block kit blocks
# this shit just gets long and i don't wanna crowd the main app file

import aptible_bot

reqs = aptible_bot.show_queue_info()
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
                    "text": "New request from " + reqs[i]['from']
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
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "All requests are granted standard permissions. Use the checkboxes to add additional permissions if needed."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "checkboxes",
                        "options": [
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Pen Test"
                                },
                                "value": "pen"
                            },
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "BCP"
                                },
                                "value": "bcp"
                            },
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "System Diagram"
                                },
                                "value": "diagram"
                            },
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "SIG Lite"
                                },
                                "value": "sig"
                            }
                        ],
                        "action_id": "perms"
                    }
                ]
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
                        "value": "yes",
                        "action_id": "approve"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject Request"
                        },
                        "value": "no",
                        "action_id": "reject"
                    }
                ]
            }
        ]
        queue_blocks.append(req_block)

print(queue_blocks)
