import pandas as pd
import os

if __name__ == '__main__':
    data_base_dir = '/home/greetlist/macd/data_storage'
    dir_list = os.listdir(data_base_dir)
    repair_df = pd.read_csv('/home/greetlist/macd/test.csv').reset_index()
    repair_date = repair_df['date']
    for d in dir_list:
        if '600316' in d:
            file_path = os.path.join(data_base_dir, d, 'stock_60m_data/kline_60m.csv')
            df = pd.read_csv(file_path)
            df = df[df['date'].isnull()]
            df['date'] = repair_date
            df.to_csv(file_path, index=False)
