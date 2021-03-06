import json
import threading

import requests

from .models import Product, WatchdogMetaDetails


class Notification:
    def __init__(self):
        settings = WatchdogMetaDetails.objects.filter(site__pk=1).first()
        if settings:
            self.private_webhook = settings.slack_webhook_uri
            self.api_token = settings.slack_api_key
            self.public_channel = settings.slack_channel_id
            self.private_channels = settings.slack_private_channel_ids

    def _private_message(self, product, product_info):
        assert isinstance(product, Product)

        for channel in self.private_channels:
            slack_msg = {
                "channel": channel,
                "blocks": [
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"{product}"},
                    },
                ],
            }

            requests.post(self.private_webhook, data=json.dumps(slack_msg))

    def _channel_message(self, product, product_info):
        assert isinstance(product, Product)

        slack_msg = {
            "channel": self.public_channel,
            "blocks": [
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Availability status has changed for the following product: \n\n"
                        f"*Product:* { product.name }\n"
                        f"*Price:* { product.price }\n"
                        f"*Availability:* { product.availability }\n"
                        f"*SKU:* { product.sku }\n"
                        f"*URL:* { product.url }\n",
                    },
                },
            ],
        }

        requests.post(self.private_webhook, data=json.dumps(slack_msg))

    def dispatch(self, product, product_info):
        thread1 = threading.Thread(
            target=self._channel_message, args=(product, product_info)
        )
        thread2 = threading.Thread(
            target=self._private_message, args=(product, product_info)
        )
        thread1.start()
        thread2.start()
