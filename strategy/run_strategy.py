import argh
import copy
from _daily_k_line_simple_strategy import *
from _ma_simple_strategy import *
from pnl_tracker import *
import os
import pandas as pd
import time
from dateutil import parser

def run_strategy(strategy, start_money, stock_code, trade_volume=100, data_period='daily'):
    res_dict_list = []
    i = 0
    if stock_code == 'all':
        for stock_code in os.listdir('/home/greetlist/macd/data_storage'):
            if stock_code.startswith('00') or stock_code.startswith('60'):
                i += 1
                start = time.time()
                #stock_code += '.XSHE' if stock_code.startswith('00') else '.XSHG'
                #res_dict_list.append(_calc_single_stock(start_money, trade_volume, data_period, stock_code))
                _calc_single_stock(start_money, trade_volume, data_period, stock_code)
                #print(i, time.time() - start)
            print('deal {} {} th'.format(stock_code, i))
    else:
        stock_code = stock_code + '.XSHE'
        #res_dict_list.append(_calc_single_stock(start_money, trade_volume, data_period, stock_code))
        _calc_single_stock(start_money, trade_volume, data_period, stock_code)
    #df = pd.DataFrame(res_dict_list)
    #df.to_csv('final.csv', index=False)

def _calc_single_stock(start_money, trade_volume, data_period, stock_code):
    klines = KLineSimpleStrategy(start_money, trade_volume, data_period, stock_code)
    mas = MASimpleStrategy(stock_code, data_period, short_period=3)
    klines.load_all_history_data()
    mas.load_all_history_data()

    kline_df = pd.read_csv(os.path.join('/home/greetlist/macd/result', stock_code, 'result_macd.csv'))
    ma_df = pd.read_csv(os.path.join('/home/greetlist/macd/result', stock_code, 'result_ma.csv'))
    total_df = kline_df.merge(ma_df, on=['date', 'close'], how='left')[['date', 'close', 'SignalMACD', 'Signal'+str(mas.short_period), 'MACD_DIFF', 'MA_DIFF'+str(mas.short_period)]]
    total_df['Signal'] = total_df[['SignalMACD', 'Signal'+str(mas.short_period)]].apply(lambda x: 'buy' if x[0] == 'buy' and x[1] == 'buy' else ('sell' if x[0] == 'sell' and x[1] == 'sell' else 'NoSignal'), axis=1)
    total_df.to_csv(os.path.join('/home/greetlist/macd/result', stock_code, 'total_result.csv'))
    return
    data_list = mas.data_df.to_dict('records')
    mas.data_df['IsTrading'] = False
    last_mid_price = 0.0
    last_signal = 0

    res_dict = {}
    res_dict['stock_code'] = stock_code
    buy_date = parser.parse('1970-01-01')
    #for ratio in [50 * x for x in range(1, 15)]:
    for ratio in [x for x in range(1, 50)]:
        klines.ratio = 33
        mas.ratio = 450
        pnl_tracker = PnlTracker(int(start_money))
        for index in range(1, len(data_list) - 1):
            mid_price = (data_list[index]['high'] + data_list[index]['low']) / 2
            #if abs(data_list[index]['MA5'] - data_list[index-1]['MA5']) > data_list[index]['close'] / ratio:
            if klines._has_buy_signal(index, data_list[index]['close']) and mas._has_buy_signal(index) and mid_price != 0:
                buy_date = parser.parse(data_list[index]['date'])
                pnl_tracker.buy(mid_price, trade_volume)
                if index == len(data_list) - 2 and last_signal == 1:
                    print('************* {}'.format(stock_code))
                print('********* {} has buy signal buy vol/close/left: {}/{}/{}'.format(data_list[index]['date'], pnl_tracker.position, mid_price, pnl_tracker.current_pos_value))
                last_signal = 0
            elif mas._has_sell_signal(index) and klines._has_sell_signal(index, data_list[index]['close']) and mid_price != 0:
                cur_date = parser.parse(data_list[index]['date'])
                if (cur_date - buy_date).days <= 0:
                    continue
                res = pnl_tracker.sell(mid_price, trade_volume)
                if index == len(data_list) - 2 and last_signal == 0:
                    print('!!!!!!!!!!!!! {}'.format(stock_code))
                last_signal = 1
                #if res > 0:
                #    print('******** {} lose money : {} ********'.format(data_list[index]['date'], res))
                print('********* {} has sell signal sell vol/close/left: {}/{}/{}'.format(data_list[index]['date'], pnl_tracker.position, mid_price, pnl_tracker.current_pos_value))
            last_mid_price = mid_price

        res_dict[ratio] = pnl_tracker.current_pos_value + pnl_tracker.position * mid_price - pnl_tracker.start_money
        if pnl_tracker.total_trade_count > 0:
            print('ratio is : {}, Final Pnl is : {} loss count is : {}, total_trade_count is : {}, loss_rate: {}, loss_money : {}'.format(ratio, pnl_tracker.current_pos_value + pnl_tracker.position * mid_price - pnl_tracker.start_money, pnl_tracker.total_loss, pnl_tracker.total_trade_count, pnl_tracker.total_loss / pnl_tracker.total_trade_count, pnl_tracker.total_loss_money))
        print(mas.data_df[-10:])
        #print('ma Total Fee is : {}'.format(pnl_tracker.total_fee))
        #print('max lose is : {}'.format(pnl_tracker.max_lose))
        break
    #final_df = mas.data_df.merge(klines.data_df, how='left', on=['date'])
    #final_df = pd.DataFrame(res_dict)
    #final_df.to_csv('final.csv')
    return res_dict

if __name__ == '__main__':
    argh.dispatch_command(run_strategy)
