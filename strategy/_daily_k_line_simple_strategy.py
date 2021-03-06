from base_strategy import *
from pnl_tracker import *
import sys
import pandas as pd
from dateutil import parser
import datetime
import os
import subprocess as sub

class KLineSimpleStrategy(BaseStrategy):
    def __init__(self, start_money, trade_volume, data_period, stock_code, dea_period=9, quick_period=12, slow_period=26):
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
        self.pnl_tracker = PnlTracker(int(start_money))
        self.trade_volume = int(trade_volume)
        self.data_period = data_period
        self.current_analyze_time = parser.parse('1970-01-01')
        self.all_diff_value = []
        self.all_macd_value = []
        self.init()
        self.init_flag = False
        self.is_today_init = False
        self.ratio = 33
        #self.load_all_history_data()

    def init(self):
        self.data_storage = '/home/greetlist/macd/data_storage'
        self.res_dir = '/home/greetlist/macd/result'
        self.k_line_data = '/home/greetlist/macd/data_storage/{}/stock_daily_data/kline_daily.csv' if self.data_period == 'daily' else '/home/greetlist/macd/data_storage/{}/stock_60m_data/kline_60m.csv'
        data_file = self.k_line_data.format(self.stock_code)
        data_df = pd.read_csv(data_file, index_col=0).reset_index()[-1000:]
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
            self._main_calc_func(float(real_data['close']), real_data['date'])
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

    def _main_calc_func(self, price, date):
        #calc EMA
        cur_ema_quick, cur_ema_slow = self._calc_k_line_ema(price)
        #diff = EMA(close, quick_period) - EMA(close, slow_period)
        cur_diff = cur_ema_quick - cur_ema_slow
        #calc DEA
        self.dea_current = self._ema_real_calc(self.dea_prev, cur_diff, self.dea_alpha)
        #calc macd MACD = 2 * DEA
        cur_macd = 2 * (cur_diff - self.dea_current)
        analyze_time = parser.parse(date)

        if (analyze_time - self.current_analyze_time).seconds >= 3600:
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
