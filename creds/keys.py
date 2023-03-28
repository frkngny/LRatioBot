# These should be parametarized later
name = ''
token = ''
trade_size = "0.01" # for OKX
fee = 0.05/100  # fee for OKX, 0.04 for binance
capital = 5000  # initial capital/budget

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
