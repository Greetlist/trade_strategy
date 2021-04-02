import pandas as pd
import argh
import glob
import os
import traceback as tb

class SingleStockMaStatistic:
    def __init__(self, stock_code):
        self.result_dir = '/home/greetlist/macd/result/'
        self.win_count = 0
        self.loss_count = 0
        self.max_percent_profit = 0
        self.max_percent_loss = 0
        self.stock_code = stock_code
        self.ma_file_path = os.path.join(self.result_dir, stock_code, 'result_ma.csv')
        self.max_win_date = None
        self.max_loss_date = None
        self.short_period = 13
        self.mid_period = 34
        self.long_period = 55
        self.check_point_date_list = []
        self.data_df = None
        self.dense_flag = False
        self.is_last_price_over_threshold = 0.00
        self._init()

    def _init(self):
        columns = [
            'date', 'close', 'low', 'volume', 
            'MA' + str(self.short_period), 'MA' + str(self.mid_period), 'MA' + str(self.long_period),
            'PREV_MA13', 'MA_DIFF13']
        self.data_df = pd.read_csv(self.ma_file_path, usecols=columns)

    def run_ma_break_statistic(self):
        data_list = self.data_df.to_dict('records')
        data_len = len(data_list)
        for i in range(1, data_len):
            if self.is_check_point(data_list, i):
                self.check_point_date_list.append(data_list[i]['date'])
                ten_days_index =  i + 5
                if ten_days_index > data_len - 1:
                    break
                if data_list[ten_days_index]['close'] > data_list[i]['close']:
                    self.win_count += 1
                    cur_percent = (data_list[ten_days_index]['close'] - data_list[i]['close']) / data_list[i]['close']
                    if cur_percent > self.max_percent_profit:
                        self.max_percent_profit = cur_percent
                        self.max_win_date = data_list[i]['date']
                else:
                    cur_percent = (data_list[ten_days_index]['close'] - data_list[i]['close']) / data_list[i]['close']
                    if cur_percent < self.max_percent_loss:
                        self.max_percent_loss = cur_percent
                        self.max_loss_date = data_list[i]['date']
                    self.loss_count += 1
        self.dense_flag = self.is_move_avg_dense(data_list, -1)
        self.is_last_price_over_threshold = data_list[-1]['close'] > 15.00

    def is_check_point(self, data, index):
        if data[index]['MA13'] != -1 and \
            data[index]['PREV_MA13'] != -1 and \
            data[index]['MA_DIFF13'] > 0 and \
            data[index-1]['MA_DIFF13'] < 0 and \
            data[index]['close'] > data[index]['MA13']:
            # self.is_move_avg_dense(data, index):
            return True
        return False

    def is_move_avg_dense(self, data_list, index):
        price_avg_threshold = data_list[index]['close'] * 0.01
        if data_list[index]['MA'+str(self.short_period)] != -1 and \
           data_list[index]['MA'+str(self.mid_period)] != -1 and \
           data_list[index]['MA'+str(self.long_period)] != -1 and \
           abs(data_list[index]['MA'+str(self.short_period)] - data_list[index]['MA'+str(self.mid_period)]) <= price_avg_threshold and \
           abs(data_list[index]['MA'+str(self.long_period)] - data_list[index]['MA'+str(self.mid_period)]) <= price_avg_threshold and \
           abs(data_list[index]['MA'+str(self.short_period)] - data_list[index]['MA'+str(self.long_period)]) <= price_avg_threshold and \
           data_list[index]['close'] >= data_list[index]['MA'+str(self.short_period)]:
            return True
        return False

    def gen_final_result(self):
        total_count = self.win_count + self.loss_count
        # print('total points is : {}'.format(total_count))
        # print('final win rate is : {}'.format(self.win_count / total_count))
        # print('final loss rate is : {}'.format(self.loss_count / total_count))
        # print('max profit : {}'.format(self.max_percent_profit))
        # print('max loss : {}'.format(self.max_percent_loss))
        result_dict = {
            'StockCode' : self.stock_code,
            'Total_count' : total_count,
            'WinCount' : self.win_count,
            'LossCount' : self.loss_count,
            'WinRate' : self.win_count / total_count if total_count != 0 else 0,
            'LossRate' : self.loss_count / total_count if total_count != 0 else 0,
            'MaxProfit' : self.max_percent_profit,
            'MaxLoss' : self.max_percent_loss,
            'MaxProfitDate' : self.max_win_date,
            'MaxLossDate' : self.max_loss_date,
            'IsMaDenseLastDay' : self.dense_flag,
            'IsPriceOverThreshold' : self.is_last_price_over_threshold,
            'CheckFlag' : self.dense_flag and self.is_last_price_over_threshold,
        }
        return result_dict

def run(dump_csv=True, stock_code='all'):
    if stock_code == 'all':
        data_list = []
        failed_stock = []
        i = 1
        for stock_code in os.listdir('/home/greetlist/macd/data_storage'):
            print(i, stock_code)
            try:
                statistic_instance = SingleStockMaStatistic(stock_code)
                statistic_instance.run_ma_break_statistic()
            except:
                failed_stock.append(stock_code)
                print(tb.format_exc())
                #raise
                continue
            data_list.append(statistic_instance.gen_final_result())
            i += 1
        if dump_csv:
            df = pd.DataFrame(data_list)
            df.to_csv('result.csv', index=False)
        print('*' * 100)
        for item in failed_stock:
            print(item)
        print('*' * 100)
    else:
        stock_code += '.XSHE' if stock_code.startswith('00') else '.XSHG'
        statistic_instance = SingleStockMaStatistic(stock_code)
        statistic_instance.run_ma_break_statistic()
        for date in statistic_instance.check_point_date_list:
            print(date)

if __name__ == '__main__':
    argh.dispatch_commands([run])

