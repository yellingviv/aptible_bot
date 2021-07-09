# a separate file for all the slack message block kit blocks
# this shit just gets long and i don't wanna crowd the main app file

new_request = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": ":sparkles: New Aptible Room Request :sparkles:"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "New request from..."
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
                            "text": "FedRAMP"
                        },
                        "value": "value-0"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "SOX"
                        },
                        "value": "value-1"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "SIG-Lite"
                        },
                        "value": "value-2"
                    }
                ],
                "action_id": "actionId-1"
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
                "value": "approve",
                "action_id": "approve_request"
            }
        ]
    }
]
