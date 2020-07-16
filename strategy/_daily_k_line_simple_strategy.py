from base_strategy import *
from pnl_tracker import *
import sys
import pandas as pd

class KLineSimpleStrategy(BaseStrategy):
    def __init__(self, start_money, trade_volume, data_period, stock_code, dea_period=9, quick_period=12, slow_period=26):
        super().__init__('daily_k_lime_simple_strategy')
        self.dea_period = dea_period
        self.quick_period = quick_period
        self.slow_period = slow_period
        self.dea_alpha = 2 / (self.dea_period+ 1)
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
        self.init()

    def init(self):
        self.data_storage = '/home/greetlist/macd/data_storage'
        self.k_line_data = '/home/greetlist/macd/data_storage/{}/stock_daily_data/kline_daily.csv' if self.data_period == 'daily' else '/home/greetlist/macd/data_storage/{}/stock_60m_data/kline_60m.csv'
        data_file = self.k_line_data.format(self.stock_code)
        data_df = pd.read_csv(data_file).rename(columns={'Unnamed: 0':'date'})
        print(data_df)
        data_df = data_df[['date', 'close', 'high', 'low', 'volume', 'money']]
        data_df = data_df.astype({
            'date' : str,
            'close' : float,
            'high' : float,
            'low' : float,
            'volume' : float,
            'money' : float})
        self.data_df = data_df

    def run(self):
        last_mid_pirce = 0
        last_status = ''
        for item in self.data_df.iterrows():
            real_data = item[1]
            #calc ema
            self.__calc_k_line_ema(real_data)
            #diff = EMA(close, quick_period) - EMA(close, slow_period)
            cur_diff = self.ema_quick_current - self.ema_slow_current
            #calc dea
            self.dea_prev = self.dea_current
            self.dea_current = self.__ema_real_calc(self.dea_current, cur_diff, self.dea_alpha)

            #define has signal
            mid_price = (real_data['high'] + real_data['low']) / 2
            if self.__has_buy_signal() and real_data['volume'] > 0:
                #if last_status == 'buy':
                #    print('******', real_data['date'])
                self.pnl_tracker.buy(mid_price, self.trade_volume)
                print('has buy signal date : {}'.format(real_data['date']))
                last_status = 'buy'
            if self.__has_sell_signal() and real_data['volume'] > 0:
                #if last_status == 'sell':
                #    print('-------', real_data['date'])
                self.pnl_tracker.sell(mid_price, self.trade_volume)
                print('has sell signal date : {}'.format(real_data['date']))
                last_status = 'sell'
            last_mid_price = mid_price

        print('mid price : {}, position : {}'.format(self.pnl_tracker.position, last_mid_price))
        print('Final Pos Value is : {}'.format(self.pnl_tracker.current_pos_value + self.pnl_tracker.position * last_mid_price))
        print('Final Pnl is : {}'.format(self.pnl_tracker.current_pos_value + self.pnl_tracker.position * mid_price - self.pnl_tracker.start_money))
        print('Total Fee is : {}'.format(self.pnl_tracker.total_fee))

    def __ema_real_calc(self, current, close, alpha):
        return close if current == 0 else close * alpha + (1 - alpha) * current

    def __calc_k_line_ema(self, data_series):
        close = data_series['close']
        high = data_series['high']
        low = data_series['low']
        volume = data_series['volume']
        money = data_series['money']

        self.ema_quick_prev = self.ema_quick_current
        self.ema_slow_prev = self.ema_slow_current
        self.ema_quick_current = self.__ema_real_calc(self.ema_quick_current, close, self.ema_quick_alpha)
        self.ema_slow_current = self.__ema_real_calc(self.ema_slow_current, close, self.ema_slow_alpha)

    def __has_buy_signal(self):
        return self.dea_prev > (self.ema_quick_prev - self.ema_slow_prev) and self.dea_current < (self.ema_quick_current - self.ema_slow_current)

    def __has_sell_signal(self):
        return self.dea_prev < (self.ema_quick_prev - self.ema_slow_prev) and self.dea_current > (self.ema_quick_current - self.ema_slow_current)
