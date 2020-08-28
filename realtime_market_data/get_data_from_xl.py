import requests
import pandas as pd
import json
import time
import os
from collections import defaultdict
import importlib
from dateutil import parser
import re
from datetime import datetime

import sys
sys.path.insert(0, '/home/greetlist/macd/strategy/')
from _daily_k_line_simple_strategy import *
from _ma_simple_strategy import *

request_url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={}&scale={}&ma=5&datalen={}'

cur_market_url = 'http://hq.sinajs.cn/list={}'
stock_dir = '/home/greetlist/macd/stock_status/'

def __get_all_stock():
    ret_list = []
    files = os.listdir(stock_dir)
    for f in files:
        if f[0] == '0' or f[0] == '3':
            ret_list.append('sz' + f[0:6])
        else:
            ret_list.append('sh' + f[0:6])
    return ret_list

all_stock_tracker = defaultdict(list)
stock_list = __get_all_stock()

def __stock_code_transform(xinlang_stock_code):
    exch_id = xinlang_stock_code[0:2]
    stock_uid = xinlang_stock_code[2:]
    return stock_uid + '.' + ('XSHE' if exch_id == 'sz' else 'XSHG')

def __init():
    global stock_list, all_stock_tracker
    for stock_code in stock_list:
        jk_stock_code = __stock_code_transform(stock_code)
        if jk_stock_code.startswith('00'):
            all_stock_tracker[stock_code].append(KLineSimpleStrategy(start_money=0, trade_volume=0, data_period='60m', stock_code=jk_stock_code))
            all_stock_tracker[stock_code].append(MASimpleStrategy(stock_code=jk_stock_code, data_period='60m'))

def __get_history_60m_market_data(stock_code):
    res = requests.get(request_url.format(stock_code, 60, 1024))
    if res.status_code != 200:
        return []
    data = json.loads(res.text)
    return data if data != None else []

def __get_current_60m_market_data(stock_code):
    res = requests.get(request_url.format(stock_code, 60, 1))
    if res.status_code != 200:
        return []
    data = json.loads(res.text)
    return data if data != None else []

def __get_current_market_data(stock_list):
    res_dict = defaultdict(dict)

    query_len = 800
    query_count = int(len(stock_list) / query_len) + 1
    for i in range(query_count):
        all_stock = ','.join(stock_list[i*query_len:(i+1)*query_len])
        final_url = cur_market_url.format(all_stock)
        res = requests.get(final_url)
        res_list = res.text.split('\n')

        pattern = re.compile(r'var hq_str_(?P<stock_code>\w{2}\d{6})=\"(?P<real_data>.*)\";')
        for item in res_list:
            if len(item) > 0:
                match = pattern.search(item)
                cur_stock_code = match.group('stock_code')
                if len(match.group('real_data')) > 0:
                    data_list = match.group('real_data').strip(',').split(',')
                    res_dict[cur_stock_code]['chinese_name'] = data_list[0]
                    res_dict[cur_stock_code]['open'] = float(data_list[1])
                    res_dict[cur_stock_code]['pre_close'] = float(data_list[2])
                    res_dict[cur_stock_code]['current_price'] = float(data_list[3])
                    res_dict[cur_stock_code]['high'] = float(data_list[4])
                    res_dict[cur_stock_code]['low'] = float(data_list[5])
                    res_dict[cur_stock_code]['volume'] = float(data_list[8])
                    res_dict[cur_stock_code]['money'] = float(data_list[9])
                    res_dict[cur_stock_code]['date'] = data_list[30]
                    res_dict[cur_stock_code]['time'] = data_list[31]
        time.sleep(4)
    return res_dict

def __has_buy_or_sell_signal(dea_prev, dea_current, ema_quick_prev, ema_quick_current, ema_slow_prev, ema_slow_current, volume):
    if dea_prev > (ema_quick_prev - ema_slow_prev) and dea_current < (ema_quick_current - ema_slow_current) and volume > 0:
        return 'buy'
    if dea_prev < (ema_quick_prev - ema_slow_prev) and dea_current > (ema_quick_current - ema_slow_current) and volume > 0:
        return 'sell'
    return 'nan'

def run():
    global stock_list, all_stock_tracker
    # deal history data
    for stock_code in stock_list:
        try:
            for strategy in all_stock_tracker[stock_code]:
                strategy.load_all_history_data()
            print('*********************** Success init {}  ***********************'.format(stock_code))
        except Exception as e:
            #print('*********************** {}\'s History Data is not prepared. ***********************'.format(stock_code))
            del all_stock_tracker[stock_code]

    while True:
        # deal current market data
        activate_stock_list = list(all_stock_tracker.keys())
        current_market_data = __get_current_market_data(activate_stock_list)
        for stock_code in activate_stock_list:
            all_strategy = all_stock_tracker[stock_code]
            if len(current_data.keys()) < 1:
                continue
            buy_signal = False
            sell_signal = False
            for single_strategy in all_strategy:
                single_strategy._main_calc_func(current_market_data['close'], current_market_data['date'] + current_market_data['time'])
                buy_signal = buy_signal and single_strategy._has_buy_signal(current_market_data['close'])
                sell_signal = sell_signal and single_strategy._has_sell_signal(current_market_data['close'])

            if buy_signal:
                print('********** {} {} has buy signal **********'.format(stock_code, current_data['chinese_name']))
            if sell_signal:
                print('********** {} {} has sell signal **********'.format(stock_code, current_data['chinese_name']))
        time.sleep(60)

if __name__ == '__main__':
    __init()
    run()
