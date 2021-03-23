import pandas as pd

result_path = '/home/greetlist/macd/result/{}/total_result.csv'

f = open('1', 'r')
profit = 0
loss = 0
basic = 0
today_total = 0
for stock_code in f.readlines():
    stock_code = stock_code[:-1]
    result_file = result_path.format(stock_code)
    df_list = pd.read_csv(result_file).to_dict('records')[-5:]
    basic += float(df_list[0]['close']) * 100
    today_total += float(df_list[-1]['close']) * 100
    print(stock_code, 'profit ' if df_list[0]['close'] < df_list[-1]['close'] else 'loss ', abs(df_list[-1]['close'] - df_list[0]['close']))
    if df_list[0]['close'] < df_list[-1]['close']:
        profit += abs(df_list[0]['close'] - df_list[-1]['close']) * 100
    else:
        loss += abs(df_list[0]['close'] - df_list[-1]['close']) * 100
print('profit : {}, loss : {}, diff : {}'.format(profit, loss, profit - loss))
print('basic : {}, today_total : {}, total profit : {}'.format(basic, today_total, today_total - basic))
