import pandas as pd
import sys
from collections import defaultdict

if __name__ == '__main__':
    res_dict = defaultdict(int)
    ma_df = pd.read_csv('final_ma.csv')
    df = pd.read_csv('final.csv')
    #for record in list(df.to_dict('records')):
    #    max_value = float('-inf')
    #    max_key = ''
    #    for key, value in record.items():
    #        if key == 'stock_code':
    #            continue
    #        if value > max_value:
    #            max_key = key
    #            max_value = value
    #    res_dict[max_key] += 1
    #for key, value in res_dict.items():
    #    print(key, value)
    com_dict = defaultdict(dict)
    for record in list(df.to_dict('records')):
        cur_sum = 0
        stock_code = ''
        for key, value in record.items():
            if key == 'stock_code':
                stock_code = value
                com_dict[value]['no_ma'] = 0
            else:
                cur_sum += value
        com_dict[stock_code]['no_ma'] = cur_sum

    for record in list(ma_df.to_dict('records')):
        cur_sum = 0
        stock_code = ''
        for key, value in record.items():
            if key == 'stock_code':
                stock_code = value
                com_dict[value]['ma'] = 0
            else:
                cur_sum += value
        com_dict[stock_code]['ma'] = cur_sum

    ma_bigger = 0
    no_ma_bigger = 0
    for stock_code, data in com_dict.items():
        print(stock_code, data)
        if data['ma'] > data['no_ma']:
            ma_bigger += 1
        else:
            no_ma_bigger += 1
    print(ma_bigger, no_ma_bigger)
