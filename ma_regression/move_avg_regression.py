import pandas as pd
import queue
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
import numpy as np

def get_n_ma_list(period, all_price):
    price_queue = queue.Queue(period)
    res = []
    for price in all_price:
        if not price_queue.full():
            price_queue.put(price)
        elif len(res) == 0:
            cur_sum = 0
            for p in list(price_queue.queue):
                cur_sum += p
            res.append(cur_sum / period)
        else:
            head_price = price_queue.get()
            last_price = res[-1]
            res.append(last_price + (price - head_price) / period)
            price_queue.put(price)
    return res

def calc_standard_error(predict, real):
    print(predict)
    print(real)
    print(np.sqrt(np.mean((predict - real) ** 2).sum()))

def main_regression():
    data_df = pd.read_csv('/home/greetlist/macd/data_storage/002142.XSHE/stock_daily_data/kline_daily.csv')
    ma_5_list_orig = get_n_ma_list(5, data_df['close'].values)
    ma_5_list = ma_5_list_orig[-100:]

    list_len = len(ma_5_list)
    x_poly = PolynomialFeatures(degree=10)
    x_features = x_poly.fit_transform(np.array([i for i in range(list_len)]).reshape(-1, 1))
    pipe = Pipeline([('poly', PolynomialFeatures(degree=3)),
              ('linear', linear_model.LinearRegression(fit_intercept=False))])
    pipe.fit(x_features, ma_5_list)
    predict_arr = pipe.predict(x_features)
    calc_standard_error(predict_arr, np.array(ma_5_list))

if __name__ == '__main__':
    main_regression()
