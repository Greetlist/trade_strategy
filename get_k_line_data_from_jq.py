from get_data_from_jq import *
import pandas as pd
import subprocess as sub
import os
from collections import defaultdict
from globals_define import *
import sys
import datetime

def mkdirp(path):
    sub.check_call('mkdir -p {}'.format(path), shell=True)

def get_failed_stock_df():
    df = pd.read_csv('./stock.csv', usecols=['stock_code', 'is_success'])
    df = df[df['is_success'] == False]
    return df

def save_stock_code_to_file():
    data_extractor = JQDataExtractor()
    res, stock_list = data_extractor.get_all_stock()
    if res == True:
        with open('./stock.csv', 'a+') as f:
            for stock in stock_list:
                f.write(stock+'\n')

def init_all_stock_query_status():
    sub.check_call('mkdir -p {}'.format(stock_status_dir), shell=True)
    stock_df = pd.read_csv('./stock.csv')
    for stock in stock_df['stock_code'].values:
        stock = stock.strip('\n')
        sub.check_call('cp ./new_trading_date.csv {}/{}.new_trading_date.csv'.format(stock_status_dir, stock), shell=True)

if __name__ == '__main__':
    data_extractor = JQDataExtractor()
    failed_stock_df = get_failed_stock_df()
    for stock_code in failed_stock_df['stock_code'].values:
        status_file = stock_status_dir + stock_code + '.new_trading_date.csv'
        status_df = pd.read_csv(status_file, usecols=['kline_daily', 'kline_60m', 'trading_date'])

        daily_failed_df = status_df[status_df['kline_daily'] == False]
        _60m_failed_df = status_df[status_df['kline_60m'] == False]

        kline_daily_failed_date = daily_failed_df['trading_date'].values
        kline_60m_failed_date = _60m_failed_df['trading_date'].values

        today = datetime.date.today()
        query_daily_k_line_flag = True
        daily_final_df = None
        for date in kline_daily_failed_date:
            date_t = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            if date_t > today:
                break
            print('query {} {} daily k line data'.format(stock_code, date))
            res, data = data_extractor.get_kline_data(stock_code, date, date, 'daily')
            if res == True:
                status_df.loc[status_df['trading_date'] == date, 'kline_daily'] = True
                daily_final_df = pd.concat([daily_final_df, data]) if daily_final_df is not None else data
            else:
                query_daily_k_line_flag = False

        if query_daily_k_line_flag:
            print('query {} all daily k line data success'.format(stock_code))
            save_file_dir = stock_daily_data_dir.format(stock_code=stock_code)
            mkdirp(save_file_dir)
            save_file_name = save_file_dir + 'kline_daily.csv'
            if daily_final_df is not None:
                daily_final_df.to_csv(save_file_name)

        #取60分钟K线，end_date必须取下一个交易日
        query_60m_k_line_flag = True
        _60m_final_df = None
        trading_date_list = list(status_df['trading_date'].values)
        for date in kline_60m_failed_date:
            date_t = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            if date_t > today:
                break
            print('query {} {} 60m k line data'.format(stock_code, date))
            next_date_index = trading_date_list.index(date) + 1
            if next_date_index >= len(trading_date_list):
                continue
            next_trading_date = trading_date_list[next_date_index]
            res, data = data_extractor.get_kline_data(stock_code, date, next_trading_date, '60m')
            if res == True:
                status_df.loc[status_df['trading_date'] == date, 'kline_60m'] = True
                _60m_final_df = pd.concat([_60m_final_df, data]) if _60m_final_df is not None else data
            else:
                query_60m_k_line_flag = False

        if query_60m_k_line_flag:
            print('query {} all 60m k line data success'.format(stock_code))
            save_file_dir = stock_60m_data_dir.format(stock_code=stock_code)
            mkdirp(save_file_dir)
            save_file_name = save_file_dir + 'kline_60m.csv'
            if _60m_final_df is not None:
                _60m_final_df.to_csv(save_file_name)

        if query_60m_k_line_flag and query_daily_k_line_flag:
            failed_stock_df.loc[failed_stock_df['stock_code'] == stock_code, 'is_success'] = True
            status_df.to_csv(status_file)
        else:
            break
        print(data_extractor.get_daily_query_quote())
    failed_stock_df.to_csv('./stock.csv')
