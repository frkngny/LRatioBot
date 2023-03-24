import json


def calculate_profit_factor(buys, price, short=False):
    if not short:
        profits = [price - buy_price for buy_price in buys]
    else:
        profits = [buy_price - price for buy_price in buys]

    plus = [p if p > 0 else 0 for p in profits]
    minus = [p if p < 0 else 0 for p in profits]
    if sum(minus) == 0:
        profit_factor = sum(plus)
    else:
        profit_factor = abs(sum(plus) / sum(minus))

    return profit_factor, profits


def load_io_params():
    # This is used for coinglass api, the json file is important
    with open('io_params.json') as json_file:
        return json.load(json_file)


def check_create_files(*args):
    # checks and creates given csv files
    import pandas as pd

    for fname in args:
        try:
            asd = pd.read_csv(fname)
        except:
            if "output" in fname:
                df = pd.DataFrame(columns=[COLUMNS.TIME, COLUMNS.LRATIO, COLUMNS.PRICE, COLUMNS.SIGNAL, COLUMNS.SOLD, COLUMNS.POSITION])
            else:
                df = pd.DataFrame(columns=[COLUMNS.TIME, COLUMNS.SYMBOL, COLUMNS.LRATIO, COLUMNS.PRICE, COLUMNS.TIME_DIFF])
            df.to_csv(fname, index=False)


class BGColors:
    # to print in color in terminal
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    PINK = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HPINK = '\033[41m'
    HGREEN = '\033[42m'
    HBLUE = '\033[44m'


class COLUMNS:
    # csv file columns
    TIME = "time"
    SYMBOL = "symbol"
    PRICE = "price"
    LRATIO = "l_ratio"
    TIME_DIFF = "time_diff_ms"
    SIGNAL = "Signal"
    SOLD = "Sold_At"
    POSITION = "position"
