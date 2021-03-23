import argh
import pandas as pd
import os
import sys

def check():
    result_dir = '/home/greetlist/macd/result/'
    stock_list = os.listdir(result_dir)
    for stock_code in stock_list:
        real_path = os.path.join(result_dir, stock_code, 'total_result.csv')
        df = pd.read_csv(real_path)
        view_list = df[-3:].to_dict('records')
        if view_list[0]['Signal'] == 'NoSignal' \
            and view_list[1]['Signal'] == 'buy' \
            and view_list[2]['Signal'] == 'buy' \
            and view_list[2]['MACD_DIFF'] != 0:
            print(stock_code)

if __name__  == '__main__':
    argh.dispatch_commands([check])
