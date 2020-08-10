from base_strategy import *
from pnl_tracker import *
import pandas as pd
from dateutil import parser

class MASimpleStrategy(BaseStrategy):
    def __init__(self, short_period, mid_period, long_period):

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
