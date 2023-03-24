# These should be parameterized later
name = '<CRYPTOARSENAL_NAME>'
token = '<CRYPTOARSENAL_TOKEN>'
trade_size = "<TRADE_SIZE>"  # generally 0.001

crypto_arsenal_payload = {
    "open_long": {"log": "{{time}} Open Long  *#{{ticker}}* at `{{close}}`", "fixed": trade_size, "action": "openLong",
                  "connectorName": name, "connectorToken": token},
    "close_long": {"log": "{{time}} Close Long  *#{{ticker}}* at `{{close}}`", "action": "closeLong",
                   "fixed": trade_size, "connectorName": name, "connectorToken": token},

    "open_short": {"connectorName": name, "connectorToken": token, "action": "openShort", "fixed": trade_size,
                   "log": "{{time}} Open Short *#{{ticker}}* at `{{close}}`"},
    "close_short": {"log": "{{time}} Close Short  *#{{ticker}}* at `{{close}}`", "action": "closeShort",
                    "fixed": trade_size, "connectorName": name, "connectorToken": token},

    "cancel_all": {"log": "{{time}} Cancel All *#{{ticker}}* at `{{close}}`", "action": "cancelAll",
                   "connectorName": name, "connectorToken": token}
}
