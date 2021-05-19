import pandas as pd
import os
import sys

sys.path.append('/home/greetlist/macd/')
from get_data_from_jq import *

if __name__ == '__main__':
    data_base_dir = '/home/greetlist/macd/data_storage'
    dir_list = os.listdir(data_base_dir)
    data_extractor = JQDataExtractor()
    for stock_code in dir_list:
        res, data = data_extractor.get_kline_data(stock_code, '2021-04-02', '2021-04-03', '60m')
        file_path = os.path.join(data_base_dir, stock_code, 'stock_60m_data/kline_60m.csv')
        df = pd.read_csv(file_path)
        data_list = data.reset_index().rename(columns={'index':'date'}).astype({'date' : str}).to_dict('records')
        for item in data_list:
            data_col = list(data.columns)
            for col in data_col:
                if col != 'date':
                    df.loc[df['date'] == item['date'], col] = item[col]
        df.to_csv(file_path, index=False)
        print(stock_code)
