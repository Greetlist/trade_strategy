import argh
import copy
from _daily_k_line_simple_strategy import *
from _ma_simple_strategy import *
from pnl_tracker import *
import os
import pandas as pd
import time

def run_strategy(strategy, start_money, stock_code, trade_volume=100, data_period='daily'):
    res_dict_list = []
    i = 0
    if stock_code == 'all':
        for stock_code in os.listdir('/home/greetlist/macd/data_storage'):
            if stock_code.startswith('00'):
                i += 1
                start = time.time()
                res_dict_list.append(_calc_single_stock(start_money, trade_volume, data_period, stock_code))
                print(i, time.time() - start)
    else:
        stock_code = stock_code + '.XSHE'
        res_dict_list.append(_calc_single_stock(start_money, trade_volume, data_period, stock_code))
    #df = pd.DataFrame(res_dict_list)
    #df.to_csv('final.csv', index=False)

def _calc_single_stock(start_money, trade_volume, data_period, stock_code):
    klines = KLineSimpleStrategy(start_money, trade_volume, data_period, stock_code)
    mas = MASimpleStrategy(stock_code, data_period, short_period=5)
    klines.load_all_history_data()
    mas.load_all_history_data()

    data_list = mas.data_df.to_dict('records')
    mas.data_df['IsTrading'] = False
    last_mid_price = 0.0

    res_dict = {}
    res_dict['stock_code'] = stock_code
    #for ratio in [50 * x for x in range(1, 15)]:
    ratio = 450
    pnl_tracker = PnlTracker(int(start_money))
    for index in range(1, len(data_list) - 1):
        mid_price = (data_list[index]['high'] + data_list[index]['low']) / 2
        if abs(data_list[index]['MA5'] - data_list[index-1]['MA5']) > data_list[index]['close'] / ratio:
            if klines._has_buy_signal(index) and data_list[index]['MA5'] - data_list[index-1]['MA5'] > 0:
                print('********* {} has buy signal'.format(data_list[index]['date']))
                pnl_tracker.buy(mid_price, trade_volume)
            elif data_list[index]['MA5'] - data_list[index-1]['MA5'] < 0 and klines._has_sell_signal(index):
                print('********* {} has sell signal'.format(data_list[index]['date']))
                pnl_tracker.sell(mid_price, trade_volume)
        last_mid_price = mid_price

    res_dict[ratio] = pnl_tracker.current_pos_value + pnl_tracker.position * mid_price - pnl_tracker.start_money
    print('ratio is : {}, ma Final Pnl is : {}'.format(ratio, pnl_tracker.current_pos_value + pnl_tracker.position * mid_price - pnl_tracker.start_money))
        #print('ma Total Fee is : {}'.format(pnl_tracker.total_fee))
    #final_df = mas.data_df.merge(klines.data_df, how='left', on=['date'])
    #final_df.to_csv('final.csv')
    return res_dict

if __name__ == '__main__':
    argh.dispatch_command(run_strategy)
