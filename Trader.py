from Utilities import *
import numpy as np
import copy
import pandas as pd
from CryptoArsenal import CryptoArsenal
from Logger import Logger
from creds.keys import trade_size, fee, capital


class Signals:
    BUY = "buy"
    SELL = "sell"


class Trader:
    def __init__(self, stored_csv):
        self.time_col = COLUMNS.TIME
        self.price_col = COLUMNS.PRICE
        self.position_col = COLUMNS.POSITION
        self.l_ratio = COLUMNS.LRATIO
        self.signal_col = COLUMNS.SIGNAL
        self.stored_data_csv = stored_csv

        self.cryptoArsenal = CryptoArsenal()
        self.logger = Logger()

        self.test_data = None
        self.output_data = None
        self.model_train = None
        self.predicted = None

        self.long_stocks = {"times": [], "prices": []}
        self.short_stocks = {"times": [], "prices": []}
        
        # define parameters for trades
        self.budget = capital
        self.buy_percent = float(trade_size)
        self.fee = fee
        self.stop_loss = 0.995
        self.pf = 1.5  # profit factor
        self.sma = 30  # moving average window
        
        self.total_profit = 0
        self.plus_profits = 0
        self.minus_profits = 0

        self.num_trades = 0

    def start_trade(self, current_data, decider_data):
        moving_avg = self.calc_ma(decider_data[-self.sma:], self.sma).iloc[-1]

        temp_decider = copy.deepcopy(decider_data)
        temp_decider.drop(temp_decider.tail(1).index, inplace=True)

        data = copy.deepcopy(current_data)

        data_time = data[self.time_col][0]
        data_price = data[self.price_col][0] * self.buy_percent
        data_signal = data[self.signal_col][0]
        data_l_ratio = data[self.l_ratio][0]

        print(f"Current time: {data_time}, price: {data_price}, signal: {data_signal}")
        flag = False
        if data_signal == Signals.BUY:
             # Signal is BUY

            # if we have budget and ma is lower than current price, open long position
            cond = moving_avg < (data_price / self.buy_percent)
            if data_price <= self.budget and cond:
                flag = self.buy_long(data_price, data_time)
            
            # if there are any short contracts, calculate profit factor and profit (if sold now) for each contract
            # if profit factor is greater than self.pf (1.5); for each contract, if profit is greater
            # than contract price * (1-stop_loss), which is contract price * 0.005, then close short position
            if len(self.short_stocks["prices"]) > 0:
                profit_factor, profits = calculate_profit_factor(self.short_stocks["prices"], data_price, True)
                if profit_factor >= self.pf:
                    shortlen = len(self.short_stocks["prices"])
                    index = 0
                    for ind in range(shortlen):
                        if profits[index] >= (self.short_stocks["prices"][index] * (1 - self.stop_loss)):
                            flag = self.sell_short(data_price, data_time, index)
                            profits.pop(index)
                        else:
                            index += 1
        else:
            # Signal is SELL

            # if there are any short contracts, calculate profit factor and profit (if sold now) for each contract
            # if profit factor is greater than self.pf (1.5); for each contract, if profit is greater
            # than contract price * (1-stop_loss), which is contract price * 0.005, then close long position
            if len(self.long_stocks["prices"]) > 0:
                profit_factor, profits = calculate_profit_factor(self.long_stocks["prices"], data_price)
                if profit_factor >= self.pf:
                    longlen = len(self.long_stocks["prices"])
                    index = 0
                    for ind in range(longlen):
                        if profits[index] >= (self.long_stocks["prices"][index] * (1 - self.stop_loss)):
                            flag = self.sell_long(data_price, data_time, index)
                            profits.pop(index)
                        else:
                            index += 1
            
            # if we have budget and ma is greater than current price, open short position
            cond1 = moving_avg > (data_price / self.buy_percent)
            if cond1 and data_price <= self.budget:
                flag = self.buy_short(data_price, data_time)
        
        # stop loss (close position) for long positions if reached defined stop loss
        long_len = len(self.long_stocks["prices"])
        index = 0
        for q in range(long_len):
            if (data_price / self.long_stocks["prices"][index]) <= self.stop_loss:
                flag = self.long_cut_loss(data_price, data_time, index)
            else:
                index += 1
        
        # stop loss (close position) for short positions if reached defined stop loss
        short_len = len(self.short_stocks["prices"])
        index = 0
        for q in range(short_len):
            if (self.short_stocks["prices"][index] / data_price) <= self.stop_loss:
                flag = self.short_cut_loss(data_price, data_time, index)
            else:
                index += 1

        if flag:
            print(f"Longs: {self.long_stocks}")
            print(f"Shorts: {self.short_stocks}")
            print(f"Budget: {self.budget}")
            print(f"Profit: {self.total_profit}")
            print(f"P Profit: {self.plus_profits}")
            print(f"M Profit: {self.minus_profits}")
            print(f"Trades: {self.num_trades}")
            self.logger.log(f"Longs: {self.long_stocks}\nShorts: {self.short_stocks}")
            
            # remove the fee for the trade from current budget
            self.budget -= (data_price * self.fee)

    def calc_ma(self, decider: pd.DataFrame, period: int):
        """
        Calculate Simple Moving Average
        :param decider: last n (period) of train data
        :param period: window
        :return: SMA mean
        """
        return decider[self.price_col].rolling(window=period).mean()

    def buy_long(self, p, t):
        r = self.cryptoArsenal.send_webhook_request("open_long", str(t).replace(".0", ""))
        if r == "ok":
            print(f"{BGColors.BLUE}Buy long {p} at {t} {BGColors.ENDC}")
            
             # store the position
            self.long_stocks["prices"].append(p)
            self.long_stocks["times"].append(t)
            
            # update stored csv file with position
            stored_data = pd.read_csv(self.stored_data_csv)
            stored_data.loc[stored_data[self.time_col] == t, self.position_col] = "long"
            stored_data.to_csv(self.stored_data_csv, index=False)

            self.budget -= p

            self.num_trades += 1
            return True
        return False

    def sell_long(self, p, t, i):
        r = self.cryptoArsenal.send_webhook_request("close_long", str(self.long_stocks['times'][i]).replace(".0", ""))
        if r == "ok":
            stock_price = self.long_stocks['prices'][i]
            stock_time = self.long_stocks['times'][i]
            prof = p - stock_price

            print(f"{BGColors.HBLUE}Sell long {stock_price} at {p} with profit: {prof} {BGColors.ENDC}")
            
            # update stored csv file with sold data
            stored_data = pd.read_csv(self.stored_data_csv)
            stored_data.loc[stored_data[self.time_col] == stock_time, "Sold_At"] = int(t)
            stored_data.to_csv(self.stored_data_csv, index=False)

            self.total_profit += prof
            self.budget += p
            if prof > 0:
                self.plus_profits += prof
            else:
                self.minus_profits += prof

            self.long_stocks['prices'].pop(i)
            self.long_stocks['times'].pop(i)
            self.num_trades += 1
            return True
        return False

    def long_cut_loss(self, p, t, i):
        r = self.cryptoArsenal.send_webhook_request("close_long", str(self.long_stocks['times'][i]).replace(".0", ""))
        if r == "ok":
            stock_price = self.long_stocks['prices'][i]
            stock_time = self.long_stocks['times'][i]
            prof = p - self.long_stocks['prices'][i]

            print(f"{BGColors.YELLOW}Long Cut loss == bought: {stock_price}, sold: {p}, loss: {prof} {BGColors.ENDC}")

            stored_data = pd.read_csv(self.stored_data_csv)
            stored_data.loc[stored_data[self.time_col] == stock_time, "Sold_At"] = int(t)
            stored_data.to_csv(self.stored_data_csv, index=False)

            self.total_profit += prof
            self.budget += p
            self.minus_profits += prof

            self.long_stocks['prices'].pop(i)
            self.long_stocks['times'].pop(i)
            self.num_trades += 1
            return True
        return False

    def buy_short(self, p, t):
        r = self.cryptoArsenal.send_webhook_request("open_short", str(t).replace(".0", ""))
        if r == "ok":
            print(f"{BGColors.GREEN}Buy short {p} at {t} {BGColors.ENDC}")

            self.short_stocks['prices'].append(p)
            self.short_stocks['times'].append(t)

            stored_data = pd.read_csv(self.stored_data_csv)
            stored_data.loc[stored_data[self.time_col] == t, self.position_col] = "short"
            stored_data.to_csv(self.stored_data_csv, index=False)

            self.budget -= p

            self.num_trades += 1
            return True
        return False

    def sell_short(self, p, t, i):
        r = self.cryptoArsenal.send_webhook_request("close_short", str(self.short_stocks['times'][i]).replace(".0", ""))
        if r == "ok":
            stock_price = self.short_stocks["prices"][i]
            stock_time = self.short_stocks["times"][i]
            prof = stock_price - p
            print(f"{BGColors.HGREEN}Sell short {stock_price} at {p} with profit: {prof} {BGColors.ENDC}")

            stored_data = pd.read_csv(self.stored_data_csv)
            stored_data.loc[stored_data[self.time_col] == stock_time, "Sold_At"] = int(t)
            stored_data.to_csv(self.stored_data_csv, index=False)

            self.total_profit += prof
            self.budget += (prof + stock_price)

            if prof > 0:
                self.plus_profits += prof
            else:
                self.minus_profits += prof
            
            self.short_stocks['prices'].pop(i)
            self.short_stocks['times'].pop(i)

            self.num_trades += 1
            return True
        return False

    def short_cut_loss(self, p, t, i):
        r = self.cryptoArsenal.send_webhook_request("close_short", str(self.short_stocks['times'][i]).replace(".0", ""))
        if r == "ok":
            stock_price = self.short_stocks["prices"][i]
            stock_time = self.short_stocks["times"][i]
            prof = stock_price - p
            print(f"{BGColors.RED}Short Cut loss == bought: {stock_price}, sold: {p}, loss: {prof} {BGColors.ENDC}")

            stored_data = pd.read_csv(self.stored_data_csv)
            stored_data.loc[stored_data[self.time_col] == stock_time, "Sold_At"] = int(t)
            stored_data.to_csv(self.stored_data_csv, index=False)

            self.total_profit += prof
            self.budget += (prof + stock_price)
            self.minus_profits += prof

            self.short_stocks['prices'].pop(i)
            self.short_stocks['times'].pop(i)
            self.num_trades += 1
            return True
        return False
