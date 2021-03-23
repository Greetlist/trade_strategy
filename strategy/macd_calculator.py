from base_strategy import *
from pnl_tracker import *
import sys
import pandas as pd
from dateutil import parser
import datetime
import os
import subprocess as sub
import traceback as tb

class MACDCalculator(BaseStrategy):
    def __init__(self, stock_code, data_period, dea_period=9, quick_period=12, slow_period=26):
        super().__init__('daily_k_lime_simple_strategy')
        self.dea_period = dea_period
        self.quick_period = quick_period
        self.slow_period = slow_period
        self.dea_alpha = 2 / (self.dea_period + 1)
        self.ema_quick_alpha = 2 / (self.quick_period + 1)
        self.ema_slow_alpha = 2 / (self.slow_period + 1)
        self.dea_prev = 0
        self.dea_current = 0
        self.ema_quick_current = 0
        self.ema_quick_prev = 0
        self.ema_slow_current = 0
        self.ema_slow_prev = 0
        self.stock_code = stock_code
        self.data_period = data_period
        self.current_analyze_time = parser.parse('1970-01-01')
        self.all_diff_value = []
        self.all_macd_value = []
        self.load_history_success = True
        self.init()
        self.init_flag = False
        self.is_today_init = False
        self.ratio = 33
        try:
            self.load_all_history_data()
        except:
            self.load_history_success = False
            print(tb.format_exc())
            print(self.data_file)

    def init(self):
        self.data_storage = '/home/greetlist/macd/data_storage'
        self.res_dir = '/home/greetlist/macd/result'
        self.k_line_data = '/home/greetlist/macd/data_storage/{}/stock_daily_data/kline_daily.csv' if self.data_period == 'daily' else '/home/greetlist/macd/data_storage/{}/stock_60m_data/kline_60m.csv'
        self.data_file = self.k_line_data.format(self.stock_code)
        if os.path.exists(self.data_file):
            #data_df = pd.read_csv(self.data_file, index_col=0).reset_index()[-250:]
            data_df = pd.read_csv(self.data_file, index_col=0).reset_index()
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
        self.data_df = data_df.fillna(0)

    def load_all_history_data(self):
        last_mid_pirce = 0
        last_status = ''
        for item in self.data_df.iterrows():
            real_data = item[1]
            self._main_calc_func(float(real_data['close']), real_data['date'], real_data)
        self.data_df['DIFF'] = self.all_diff_value
        self.data_df['MACD'] = self.all_macd_value
        self.data_df['PREV_MACD'] = [-1] + self.all_macd_value[:-1]
        self.data_df['MACD_DIFF'] = self.data_df['MACD'] - self.data_df['PREV_MACD']
        self.data_df['SignalMACD'] = self.data_df[['close', 'MACD_DIFF']].apply(lambda x: 'buy' if x[1] >= 0.05 * x[0] / self.ratio else ('sell' if x[1] < -0.05 * x[0] / self.ratio else 'NoSignal'), axis=1)
        #self.data_df = None
        sub.check_call('mkdir -p {}'.format(os.path.join(self.res_dir, self.stock_code)), shell=True)
        self.data_df.to_csv(os.path.join(self.res_dir, self.stock_code, 'result_macd.csv'), index=False)
        self.init_flag = True
        self.is_today_init = True

    def _main_calc_func(self, price, date, real_data):
        #calc EMA
        cur_ema_quick, cur_ema_slow = self._calc_k_line_ema(price)
        #diff = EMA(close, quick_period) - EMA(close, slow_period)
        cur_diff = cur_ema_quick - cur_ema_slow
        #calc DEA
        self.dea_current = self._ema_real_calc(self.dea_prev, cur_diff, self.dea_alpha)
        #calc macd MACD = 2 * DEA
        cur_macd = 2 * (cur_diff - self.dea_current)
        try:
            analyze_time = parser.parse(date)
        except:
            print(self.data_file, real_data)
            self.data_df.to_csv('test.csv', index=False)
            raise

        if (analyze_time - self.current_analyze_time).total_seconds() >= 3600:
            self.all_diff_value.append(cur_diff)
            self.all_macd_value.append(cur_macd)
            if not self.is_today_init:
                self.ema_quick_prev = cur_ema_quick
                self.ema_slow_prev = cur_ema_slow
                self.dea_prev = self.dea_current
            else:
                self.is_today_init = False
            self.current_analyze_time = parser.parse(date)
        else:
            self.all_diff_value[-1] = cur_diff
            self.all_macd_value[-1] = cur_macd

    def _calc_k_line_ema(self, close):
        ema_quick_current = self._ema_real_calc(self.ema_quick_prev, close, self.ema_quick_alpha)
        ema_slow_current = self._ema_real_calc(self.ema_slow_prev, close, self.ema_slow_alpha)
        return ema_quick_current, ema_slow_current

    def _ema_real_calc(self, prev, close, alpha):
        return close if prev == 0 else close * alpha + (1 - alpha) * prev

    def _has_buy_signal(self, index, price):
        if index > 0 and index < len(self.all_macd_value):
            return self.all_macd_value[index] - self.all_macd_value[index-1] >= 0.05 * price / self.ratio
            #return self.all_macd_value[index] - self.all_macd_value[index-1] >= 0.05

    def _has_sell_signal(self, index, price):
        if index > 0 and index < len(self.all_macd_value):
            return self.all_macd_value[index] - self.all_macd_value[index-1] < -0.05 * price / self.ratio
            #return self.all_macd_value[index] - self.all_macd_value[index-1] < -0.05

    def _realtime_has_buy_signal(self, price):
        return self.all_macd_value[-1] - self.all_macd_value[-2] >= 0.05 * price / self.ratio

    def _realtime_has_sell_signal(self, price):
        return self.all_macd_value[-1] - self.all_macd_value[-2] < -0.05 * price / self.ratio

    def _macd_has_buy_signal(self, index):
        if index > 0 and index < len(self.all_macd_value):
            if self.all_macd_value[index] > 0 and self.all_macd_value[index-1] < 0 and self._has_buy_signal(index):
                return True
        return False

    def _macd_has_sell_signal(self, index):
        if index > 0 and index < len(self.all_macd_value):
            if self.all_macd_value[index] <= 0 and self.all_macd_value[index-1] >= 0 and self._has_sell_signal(index):
                return True
        return False
