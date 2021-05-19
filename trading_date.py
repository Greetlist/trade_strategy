import pandas as pd
import argh
from datetime import datetime

class TradingDate:
    def __init__(self):
        self.trading_date_csv_path = '/home/greetlist/macd/trading_date.csv'
        self.trading_date_df = pd.read_csv(self.trading_date_csv_path, dtype={'trading_date' : str})

    # args date_str format is : yy-mm-dd, return yy-mm-dd
    def get_next_trading_date(self, date_str):
        return self.__do_get_trading_date(date_str, 1)

    # args date_str format is : yy-mm-dd, return yy-mm-dd
    def get_prev_trading_date(self, date_str):
        return self.__do_get_trading_date(date_str, -1)

    def __do_get_trading_date(self, date_str, offset):
        csv_trading_date = date_str.replace('-', '')
        today_df = self.trading_date_df.loc[self.trading_date_df['trading_date'] == csv_trading_date]
        assert len(today_df) == 1, 'Trading date csv is wrong, Please Check!!'
        target_day_index = list(today_df.reset_index(drop=False)['index'].values)[0] + offset
        assert (target_day_index >= 0 and target_day_index < len(self.trading_date_df)), 'Index Calc is Wrong, calced index is : {}'.format(target_day_index)
        target_date_str = self.trading_date_df.loc[target_day_index]['trading_date']
        yy = target_date_str[0:4]
        mm = target_date_str[4:6]
        dd = target_date_str[6:]
        print(yy + '-' + mm + '-' + dd)

if __name__ == '__main__':
    td = TradingDate()
    #date_str = datetime.now().strftime('%Y-%m-%d')
    date_str = '2021-04-26'
    td.get_next_trading_date(date_str)
    td.get_prev_trading_date(date_str)
