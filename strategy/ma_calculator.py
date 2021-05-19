from base_strategy import *
from pnl_tracker import *
import pandas as pd
from dateutil import parser
import datetime
import os
import subprocess as sub
import traceback as tb

class MACalculator(BaseStrategy):
    def __init__(self, stock_code, data_period, ratio=450, short_period=13, mid_period=34, long_period=55):
        self.data_period = data_period
        #self.total_period_list = [4, short_period, 6, 7, mid_period, long_period]
        self.short_period = short_period
        self.mid_period = mid_period
        self.long_period = long_period
        self.total_period_list = [short_period, mid_period, long_period]
        self.price_queues = [list() for period in self.total_period_list]
        self.ma_list = [list() for period in self.total_period_list]
        self.cur_ma_value = [-1] * len(self.total_period_list)
        self.stock_code = stock_code
        self.load_history_success = True
        self.init()
        self.ratio = ratio
        self.current_analyze_time = parser.parse('1970-01-01')
        self.init_flag = False
        try:
            self.load_all_history_data()
        except:
            print('*' * 100)
            print(self.stock_code)
            print(tb.format_exc())
            print('*' * 100)
            self.load_history_success = False

    def init(self):
        self.data_storage = '/home/greetlist/macd/data_storage'
        self.res_dir = '/home/greetlist/macd/result'
        self.k_line_data = '/home/greetlist/macd/data_storage/{}/stock_daily_data/kline_daily.csv' if self.data_period == 'daily' else '/home/greetlist/macd/data_storage/{}/stock_60m_data/kline_60m.csv'
        self.data_file = self.k_line_data.format(self.stock_code)
        if os.path.exists(self.data_file):
            #data_df = pd.read_csv(self.data_file, index_col=0).reset_index()[-250:]
            data_df = pd.read_csv(self.data_file, index_col=0).reset_index()
            self.data_df = data_df.fillna(0)
            data_df = data_df.dropna()
            # no_nan_df = data_df.dropna()
            # if len(no_nan_df) != len(data_df):
                # data_df = pd.DataFrame(columns=['date', 'close', 'high', 'low', 'volume', 'money'])
                # self.load_history_success = False
        else:
            data_df = pd.DataFrame(columns=['date', 'close', 'high', 'low', 'volume', 'money'])
            self.load_history_success = False

        data_df = data_df.astype({
            'date' : str,
            'close' : float,
            'high' : float,
            'low' : float,
            'volume' : float,
            'money' : float})

    def _main_calc_func(self, price, date):
        analyze_time = parser.parse(date)
        for i in range(len(self.total_period_list)):
            if len(self.price_queues[i]) <= self.total_period_list[i]:
                self.price_queues[i].append(price)
                if len(self.price_queues[i]) < self.total_period_list[i]:
                    self.ma_list[i].append(self.cur_ma_value[i])

                # init
                if len(self.price_queues[i]) == self.total_period_list[i]:
                    if self.cur_ma_value[i] < 0:
                        cur_sum = 0
                        for single_price in self.price_queues[i]:
                            cur_sum += single_price
                        self.cur_ma_value[i] = cur_sum / self.total_period_list[i]
                        self.ma_list[i].append(self.cur_ma_value[i])
                if len(self.price_queues[i]) == self.total_period_list[i] + 1:
                    self.cur_ma_value[i] = \
                        self.ma_list[i][-1] + (self.price_queues[i][-1] - self.price_queues[i][0]) / self.total_period_list[i]
                    self.ma_list[i].append(self.cur_ma_value[i])
                    self.current_analyze_time = analyze_time
            else:
                if (analyze_time - self.current_analyze_time).total_seconds() >= 3600:
                    self.price_queues[i].append(price)
                    self.price_queues[i] = self.price_queues[i][1:]
                    self.cur_ma_value[i] = \
                        self.ma_list[i][-1] + (self.price_queues[i][-1] - self.price_queues[i][0]) / self.total_period_list[i]
                    self.ma_list[i].append(self.cur_ma_value[i])
                # for realtime
                else:
                    self.price_queues[i][-1] = price
                    cur_ma_value = self.ma_list[i][-2] + (self.price_queues[i][-1] - self.price_queues[i][0]) / self.total_period_list[i]
                    self.ma_list[i][-1] = cur_ma_value
        if (analyze_time - self.current_analyze_time).total_seconds() >= 3600:
            self.current_analyze_time = analyze_time

    def load_all_history_data(self):
        for item in self.data_df.iterrows():
            real_data = item[1]
            self._main_calc_func(real_data['close'], real_data['date'])

        for i in range(len(self.total_period_list)):
            period_str = str(self.total_period_list[i])
            ori_str = 'MA' + period_str
            prev_str = 'PREV_MA' + period_str
            diff_str = 'MA_DIFF' + period_str
            self.data_df[ori_str] = self.ma_list[i]
            self.data_df[prev_str] = [-1] + self.ma_list[i][:-1]
            self.data_df[diff_str] = self.data_df[ori_str] - self.data_df[prev_str]
            self.data_df['Signal'+period_str] = self.data_df[['close', diff_str]].apply(lambda x: 'buy' if x[1] >= x[0] / self.ratio else ('sell' if x[1] < -x[0] / self.ratio else 'NoSignal'), axis=1)
        #self.data_df = None
        sub.check_call('mkdir -p {}'.format(os.path.join(self.res_dir, self.stock_code)), shell=True)
        self.data_df.to_csv(os.path.join(self.res_dir, self.stock_code, 'result_ma.csv'), index=False)
        self.init_flag = True

    def _has_buy_signal(self, index):
        if index > 0 and index < len(self.ma_list[0]):
            return self.ma_list[0][index] - self.ma_list[0][index-1] > self.data_df['close'].values[index] / self.ratio

    def _has_sell_signal(self, index):
        if index > 0 and index < len(self.ma_list[0]):
            return self.ma_list[0][index] - self.ma_list[0][index-1] < -(self.data_df['close'].values[index] / self.ratio)

    def _realtime_has_buy_signal(self, price):
        price = self.price_queues[-2]
        return self.ma_list[0][-1] - self.ma_list[0][-2] >= price / self.ratio

    def _realtime_has_sell_signal(self, price):
        price = self.price_queues[-2]
        return self.ma_list[0][-1] - self.ma_list[0][-2] < -(price / self.ratio)

if __name__ == '__main__':
    ma = MASimpleStrategy('002142.XSHE', '60m')
