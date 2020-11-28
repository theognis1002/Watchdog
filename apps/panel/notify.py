from .models import WatchdogSettings
import requests
import json


class Notification:
    def __init__(self):
        settings = WatchdogSettings()
        self.private_webhook = settings.slack_webhook_uri
        self.SLACK_MAIN_TOKEN = settings.slack_api_key
        self.private_channel = settings.slack_channel_id

    def message(self, message):

        slack_msg = {
            "channel": self.private_channel,
            "blocks": [
                {"type": "divider"},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"{message}"}},
            ],
        }

        requests.post(self.private_webhook, data=json.dumps(slack_msg))
