import pandas as pd
import glob


for f in glob.glob('/home/greetlist/macd/data_storage/*/stock_daily_data/kline_daily.csv'):
    df = pd.read_csv(f)
    df_unique = df.drop_duplicates(subset=['date'])
    if len(df) != len(df_unique):
        print(f)
        #df_unique.to_csv(f, index=False)
