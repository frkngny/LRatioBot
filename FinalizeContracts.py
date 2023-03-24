from creds.keys import crypto_arsenal_payload
from CryptoArsenal import CryptoArsenal

crypto = CryptoArsenal()
#Long:  {'times': [], 'prices': [26.3459, 26.3134, 26.291400000000003, 26.311400000000003, 26.295, 26.306700000000003, 26.312900000000003, 26.3723, 26.3643, 26.3564, 26.3343, 26.3413, 26.341400000000004, 26.3435, 26.358700000000002, 26.3401, 26.343799999999998, 26.3385, 26.3353]}
print(crypto.send_webhook_request("close_long", "1679076879549.0"))
