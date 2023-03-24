import requests
from creds.keys import crypto_arsenal_payload


class CryptoArsenal:
    def __init__(self):
        self.URL = 'https://api.crypto-arsenal.io/trading-signal/webhook'

    def send_webhook_request(self, position: str, orderId: str):
        """
        Creates an order request.
        :param position: open_long, close_long, open_short, close_short, cancel_all
        :param orderId: exchange id
        :return: response
        """
        payload = crypto_arsenal_payload[position]
        payload["clientOrderId"] = orderId
        response = requests.post(self.URL, json=payload)
        return response.text
