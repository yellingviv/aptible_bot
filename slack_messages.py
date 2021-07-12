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
                        "value": "fed"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "SOX"
                        },
                        "value": "sox"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "SIG-Lite"
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
                "value": "approve",
                "action_id": "approve"
            }
        ]
    }
]
