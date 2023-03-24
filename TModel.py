from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
from Utilities import COLUMNS


class TModel:
    def __init__(self, train_data, input_data):
        self.time_col = COLUMNS.TIME
        self.price_col = COLUMNS.PRICE
        self.l_ratio = COLUMNS.LRATIO
        self.output_data = None

        self.train_data = train_data
        self.test_data = input_data

        self.model = None
        self.predicted = None

    def create_train_and_test(self):
        # Read dataset
        data = self.train_data[[self.time_col, self.l_ratio, self.price_col]]
        data = data.sort_values(self.time_col)
        data.index = [i for i in range(len(data.index))]

        # load test data (current data)
        test_data = self.test_data[[self.time_col, self.l_ratio, self.price_col]]
        test_data = test_data.sort_values(self.time_col)
        test_data.index = [i for i in range(len(data.index) + 1, len(data.index) + 1 + len(test_data.index))]

        self.train_data = data
        self.test_data = test_data.iloc[-1:]

    def create_model(self):
        y = self.train_data[self.l_ratio]
        self.model = ARIMA(y, order=(1, 1, 0))  # 807, enforce_stationarity=False, enforce_invertibility=False
        self.model = self.model.fit()

    def create_prediction(self):
        # get the next forecast from model, the predict the signal

        y_pred = self.model.get_forecast(1)
        y_pred_df = y_pred.conf_int(alpha=0.05)
        y_pred_df["Predictions"] = self.model.predict(start=y_pred_df.index[0], end=y_pred_df.index[-1])
        y_pred_df.index = self.test_data.index
        self.predicted = y_pred_df["Predictions"]

        # arima_rmse = np.sqrt(mean_squared_error(self.test_data[self.l_ratio].values, y_pred_df["Predictions"]))
        # print("RMS: ", arima_rmse)

    def create_buy_sell(self):
        """
        Depending on the forecast, create sell or buy signal comparing current l-ratio
        :return: current data with buy/sell signal
        """
        self.create_prediction()

        self.test_data[COLUMNS.SIGNAL] = np.where(self.test_data[self.l_ratio] > self.predicted, 'sell', 'buy')
        self.test_data.index = [i for i in range(len(self.test_data.index))]

        return self.test_data
