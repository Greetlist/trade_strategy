from base_strategy import *
from pnl_tracker import *
import pandas as pd
from dateutil import parser

class ROCSimpleStrategy(BaseStrategy):
    def __init__(self, roc_peroid=12, roc_ma_peroid=6, roc_ema_peroid=9):
        self.pnl_tracker = PnlTracker(int(start_money))
        self.current_analyze_time = None
        self.simple_roc_peroid = roc_peroid
        self.simple_roc_ma_peroid = roc_ma_peroid
        self.simple_roc_ema_peroid = roc_ema_peroid
        self.simple_roc_ema_alpha = 2 / (roc_ema_peroid + 1)
        self.init_ema = False
        self.price_queue = []
        self.roc_queue = []
        self.current_roc = 0.0
        self.current_roc_ma = 0.0
        self.current_roc_ema = 0.0

    def init(self):
        self.data_storage = '/home/greetlist/macd/data_storage'
        self.k_line_data = '/home/greetlist/macd/data_storage/{}/stock_daily_data/kline_daily.csv' if self.data_period == 'daily' else '/home/greetlist/macd/data_storage/{}/stock_60m_data/kline_60m.csv'
        data_file = self.k_line_data.format(self.stock_code)
        data_df = pd.read_csv(data_file, index_col=0)#.rename(columns={'Unnamed: 0':'date'})
        data_df = data_df[['date', 'close', 'high', 'low', 'volume', 'money']]
        data_df = data_df.astype({
            'date' : str,
            'close' : float,
            'high' : float,
            'low' : float,
            'volume' : float,
            'money' : float})
        self.data_df = data_df

    def calc_simple_roc(self, price):
        if len(self.price_queue) < self.simple_roc_peroid:
            self.price_queue.append(price)
        else:
            self.current_roc = (price - self.price_queue[0]) / self.price_queue[0] * 100
            self.price_queue = self.price_queue[1:]
            self.price_queue.append(price)

    def calc_simple_roc_ma(self):
        self.roc_queue.append(self.current_roc)
        if len(self.roc_queue) >= self.simple_roc_ma_peroid:
            self.current_roc_ma = sum(self.roc_queue) / self.simple_roc_ma_peroid
            self.roc_queue = self.roc_queue[1:]

    def calc_simple_roc_ema(self):
        if not self.init_ema:
            self.current_roc_ema = self.current_roc * self.simple_roc_ema_alpha + (1 - self.simple_roc_ema_alpha) * self.current_roc_ema
            self.init_ema = True

    def calc_avg_price(self, trade_volume, trade_money):
        return trade_money / trade_volume

    def run(self):
        for item in self.data_df.iterrows():
            real_data = item[1]
            avg_price = self.calc_avg_price(real_data['volume'], real_data['money'])
            self.calc_simple_roc(avg_price)
            self.calc_simple_roc_ma()
            self.calc_simple_roc_ema()
