import datetime
import time

import pandas as pd
from TModel import TModel
from DataHandler import DataHandler
from Trader import Trader
from Utilities import check_create_files, COLUMNS


class Main:
    def __init__(self):
        self.time_col = COLUMNS.TIME
        self.price_col = COLUMNS.PRICE
        self.l_ratio = COLUMNS.LRATIO

        # define csv files, please make sure that your csv file is empty or doesn't exist before starting.
        self.train_csv = "training_data_test.csv"
        self.input_csv = "input_data_test.csv"
        self.output_csv = "output_stored_test.csv"

        # this checks the csv files and creates if not found
        check_create_files(self.train_csv, self.input_csv, self.output_csv)

        self.trader = Trader(self.output_csv)
        self.dataMngr = DataHandler("selenium")
        # time interval for the next operation (get data and take action to buy/sell)
        # if 1 second pass for the operation, it waits 4 seconds for the next
        self.time_interval = 5

        self.model = None
        self.signaled_data = None

        self.training_data = None
        self.training_decider_data = None
        self.input_data = None

    def train_and_pred(self):
        """
        Train the model and get forecast result
        :return: the result of forecast with buy/sell signal
        """
        self.model = TModel(self.training_data, self.input_data)
        self.model.create_train_and_test()
        self.model.create_model()
        self.update_train_data()
        return self.model.create_buy_sell()

    def update_train_data(self):
        """
        Update training data with the new incoming data
        """
        self.training_data = pd.concat([self.training_data, self.input_data])
        self.training_data.to_csv(self.train_csv, index=False)

    def create_data(self):
        # training data, get last 5000
        data = pd.read_csv(self.train_csv)
        if len(data) > 5000:
            data = data[-5000:]

        data = data.sort_values(self.time_col)
        data.index = [i for i in range(len(data.index))]

        self.training_data = data

        # get the last 50 of the training data to calculate moving average
        if len(data) > 50:
            self.training_decider_data = data[-50:]
        else:
            self.training_decider_data = data

        # the input data is the last data which we get from API
        # in data handler, we get data and put it to a csv
        # here we get the last data in the csv file
        input_data = pd.read_csv(self.input_csv)
        input_data = input_data.sort_values(self.time_col)
        input_data.index = [i for i in range(len(data.index) + 1, len(data.index) + 1 + len(input_data.index))]
        self.input_data = input_data.iloc[-1:]

    def trade(self, input_data):
        self.trader.start_trade(input_data, self.training_decider_data)

    def init_process(self):
        # if there is no data in training set, collect 5000 data first
        df_len = len(pd.read_csv(self.train_csv))
        if df_len < 5000:
            k = 0
            while k < 5000:
                strt = time.perf_counter()
                try:
                    self.dataMngr.scrape_data_and_store(self.train_csv)
                    k += 1
                except KeyboardInterrupt:
                    break
                except:
                    self.dataMngr.refresh_selenium()
                    time.sleep(5)
                    continue

                end = time.perf_counter()
                if end - strt < self.time_interval:
                    time.sleep(self.time_interval - (end - strt))

        # start operation continuously
        while True:
            strt = time.perf_counter()
            try:
                # get current data
                self.dataMngr.scrape_data_and_store(self.input_csv)
            except:
                # refresh in case any error in browser or web page
                self.dataMngr.refresh_selenium()
                continue

            try:
                # prepare train and current data
                self.create_data()

                # train model and save into stored csv file.
                self.signaled_data = self.train_and_pred()
                stored = pd.read_csv(self.output_csv)
                stored = pd.concat([stored, self.signaled_data])
                stored.to_csv(self.output_csv, index=False)

                # make a trade depending on signal
                self.trade(self.signaled_data)
            except KeyboardInterrupt:
                # you can press CTRL+C to stop, don't forget to sell the contracts.
                # The contracts are stored in latest log file
                break
            except:
                print("Long: ", self.trader.long_stocks)
                print("Short: ", self.trader.short_stocks)
                print("Budget: ", self.trader.budget)
                print("Profit: ", self.trader.total_profit)
                print("P Profits: ", self.trader.plus_profits)
                print("M Profits: ", self.trader.minus_profits)
                try:
                    print("Profit Factor: ", abs(self.trader.plus_profits / self.trader.minus_profits))
                except:
                    pass
            # wait for the next operation
            end = time.perf_counter()
            if end - strt < self.time_interval:
                time.sleep(self.time_interval - (end - strt))


start = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# start process
mn = Main()
mn.init_process()

print("Start: ", start)
print("End: ", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
