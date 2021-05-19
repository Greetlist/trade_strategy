import pandas as pd
import glob
import os
import argh
import sys
sys.path.append('/home/greetlist/macd/')
from get_data_from_jq import *

STATUS_FILE_PATH = '/home/greetlist/macd/stock_status'
MARKET_DATA_PATH = '/home/greetlist/macd/data_storage'


def replace_status_wrong_date():
    for f in os.listdir(STATUS_FILE_PATH):
        status_file = os.path.join(STATUS_FILE_PATH, f)
        df = pd.read_csv(status_file)
        df.loc[df['trading_date'] == '2021-04-05', 'trading_date'] = '2021-04-02'
        df.to_csv(status_file, index=False)

def remove_status_wrong_date():
    for f in os.listdir(STATUS_FILE_PATH):
        status_file = os.path.join(STATUS_FILE_PATH, f)
        df = pd.read_csv(status_file)
        df = df[(df['trading_date'] != '2021-09-20') & (df['trading_date'] != '2021-05-04') & (df['trading_date'] != '2021-05-05')]
        df.to_csv(status_file, index=False)

def replace_market_data_date():
    data_extractor = JQDataExtractor()
    for market_data_file in glob.glob(os.path.join(MARKET_DATA_PATH, '*', 'stock_daily_data', 'kline_daily.csv')):
        df = pd.read_csv(market_data_file)
        stock_code = market_data_file.split('/')[5]
        res, data = data_extractor.get_kline_data(stock_code, '2021-04-02', '2021-04-02', 'daily')
        if res == True:
            data = data.reset_index().rename(columns={'index':'date'}).astype({'date' : str})
            daily_final_df = pd.concat([df, data]) if df is not None else data
            daily_final_df.sort_values(by=['date'], inplace=True)
            daily_final_df.to_csv(market_data_file, index=False)
        else:
            print(market_data_file)

if __name__ == '__main__':
    argh.dispatch_commands([replace_status_wrong_date, remove_status_wrong_date, replace_market_data_date])
