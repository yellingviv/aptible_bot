import os
from slack_bolt import App

# initialize app with slack bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Add functionality here
# @app.event("app_home_opened") etc


# start the app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
