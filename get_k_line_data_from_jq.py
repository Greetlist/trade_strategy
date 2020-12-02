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

def get_all_stock_code_from_jq():
    data_extractor = JQDataExtractor()
    res, stock_list = data_extractor.get_all_stock()
    df = pd.DataFrame()
    df['stock_code'] = stock_list
    df['is_success'] = False
    if res == True:
        df.to_csv('stock.csv', index=False)

def init_all_stock_query_status():
    sub.check_call('mkdir -p {}'.format(stock_status_dir), shell=True)
    stock_df = pd.read_csv('./stock.csv')
    for stock in stock_df['stock_code'].values:
        stock = stock.strip('\n')
        sub.check_call('cp ./new_trading_date.csv {}/{}.new_trading_date.csv'.format(stock_status_dir, stock), shell=True)

def get_next_trading_day(today_str):
    trading_date_df = pd.read_csv('./new_trading_date.csv', usecols=['trading_date'])
    trading_date_list = list(trading_date_df['trading_date'].values)
    next_date_index = trading_date_list.index(date) + 1
    if next_date_index >= len(trading_date_list):
        next_date_index = len(trading_date_list) - 1
    next_trading_date = trading_date_list[next_date_index]
    return next_trading_date

def get_prev_trading_day(today_str):
    trading_date_df = pd.read_csv('./new_trading_date.csv', usecols=['trading_date'])
    trading_date_list = list(trading_date_df['trading_date'].values)
    next_date_index = trading_date_list.index(date) - 1
    if next_date_index < 0:
        next_date_index = 0
    next_trading_date = trading_date_list[next_date_index]
    return next_trading_date

if __name__ == '__main__':
    # init, only run once
    # init_all_stock_query_status()
    # sys.exit(1)

    data_extractor = JQDataExtractor()
    failed_stock_df = get_failed_stock_df()
    failed_stock_df = failed_stock_df[(failed_stock_df['stock_code'].str.startswith('00')) | (failed_stock_df['stock_code'].str.startswith('60'))]
    for stock_code in failed_stock_df['stock_code'].values:
        status_file = stock_status_dir + stock_code + '.new_trading_date.csv'
        status_df = pd.read_csv(status_file, usecols=['kline_daily', 'kline_60m', 'trading_date'])

        daily_failed_df = status_df[status_df['kline_daily'] == False]
        _60m_failed_df = status_df[status_df['kline_60m'] == False]

        kline_daily_failed_date = daily_failed_df['trading_date'].values
        kline_60m_failed_date = _60m_failed_df['trading_date'].values

        # 拉取日K线数据
        # #拉取到昨天为止的数据,如果之前有拉过这只股票的，读历史文件再concat，最后再写文件
        today = datetime.date.today()
        query_daily_k_line_flag = True
        # save_file_dir = stock_daily_data_dir.format(stock_code=stock_code)
        # save_file_name = save_file_dir + 'kline_daily.csv'
        # daily_final_df = pd.read_csv(save_file_name, index_col=0) if os.path.exists(save_file_name) else None
        # for date in kline_daily_failed_date:
            # date_t = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            # # >=防止拉取到今天的数据
            # if date_t >= today:
                # break
            # print('query {} {} daily k line data'.format(stock_code, date))
            # res, data = data_extractor.get_kline_data(stock_code, date, date, 'daily')
            # data = data.reset_index().rename(columns={'index':'date'}).astype({'date' : str})
            # if res == True:
                # status_df.loc[status_df['trading_date'] == date, 'kline_daily'] = True
                # daily_final_df = pd.concat([daily_final_df, data]) if daily_final_df is not None else data
            # else:
                # query_daily_k_line_flag = False

        # if query_daily_k_line_flag:
            # print('query {} all daily k line data success'.format(stock_code))
            # mkdirp(save_file_dir)
            # if daily_final_df is not None:
                # daily_final_df.reset_index(drop=True).to_csv(save_file_name, index=False)

        #取60分钟K线，end_date必须取下一个交易日
        #拉取到昨天为止的数据,如果之前有拉过这只股票的，读历史文件再concat，最后再写文件
        query_60m_k_line_flag = True
        save_file_dir = stock_60m_data_dir.format(stock_code=stock_code)
        save_file_name = save_file_dir + 'kline_60m.csv'
        _60m_final_df = pd.read_csv(save_file_name) if os.path.exists(save_file_name) else None

        for date in kline_60m_failed_date:
            date_t = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            # >=防止拉取到今天的数据
            if date_t >= today:
                break
            next_trading_date = get_next_trading_day(date)
            print('query {} {} 60m k line data'.format(stock_code, date))
            res, data = data_extractor.get_kline_data(stock_code, date, next_trading_date, '60m')
            data = data.reset_index().rename(columns={'index':'date'}).astype({'date' : str})
            if res == True:
                status_df.loc[status_df['trading_date'] == date, 'kline_60m'] = True
                _60m_final_df = pd.concat([_60m_final_df, data]) if _60m_final_df is not None else data
            else:
                query_60m_k_line_flag = False

        if query_60m_k_line_flag:
            print('query {} all 60m k line data success'.format(stock_code))
            mkdirp(save_file_dir)
            if _60m_final_df is not None:
                _60m_final_df.reset_index(drop=True).to_csv(save_file_name, index=False)

        if query_60m_k_line_flag and query_daily_k_line_flag:
            status_df.to_csv(status_file, index=False)
        else:
            break
        print(data_extractor.get_daily_query_quote())
