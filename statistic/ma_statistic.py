import pandas as pd
import argh
import glob
import os
import traceback as tb
import subprocess as sub
from datetime import datetime
import sys

sys.path.extend(['/home/greetlist/macd/', '/home/greetlist/macd/strategy'])
from trading_date import *
from pnl_tracker import *

dump_file_base_dir = '/data/tmp/daily_ma_result/'

class SingleStockMaStatistic:
    def __init__(self, stock_code):
        self.result_dir = '/home/greetlist/macd/result/'
        self.dump_file_base_dir = dump_file_base_dir
        self.dump_file_name = 'ma_statistic_result.csv'
        self.diff_file_name = 'diff.csv'
        self.stock_code = stock_code
        self.ma_file_path = os.path.join(self.result_dir, stock_code, 'result_ma.csv')
        self.short_period = 13
        self.mid_period = 34
        self.long_period = 55
        self.buy_signal_date = []
        self.data_df = None
        self.dense_flag = False #是否均线密集
        self.is_last_price_over_threshold = 0.00
        self.is_last_price_over_short_ma_avg = False
        self.price_threshold = 12.00
        self.trading_date_helper = TradingDate()
        self.last_check_point_index = -1 #为了避免重复信号
        self.pnl_tracker = PnlTracker(start_money=100000)
        self.loss_threshold = 0.05
        self.profit_threshold = 3 * self.loss_threshold
        self._init()

    def _init(self):
        columns = [
            'date', 'close', 'low', 'volume', 
            'MA' + str(self.short_period), 'MA' + str(self.mid_period), 'MA' + str(self.long_period),
            'PREV_MA'+str(self.short_period), 'MA_DIFF'+str(self.short_period)]
        self.data_df = pd.read_csv(self.ma_file_path, usecols=columns)

    def run_ma_break_statistic(self):
        data_list = self.data_df.to_dict('records')
        data_len = len(data_list)
        for i in range(1, data_len):
            if self.has_buy_signal(data_list, i):
                self.pnl_tracker.buy(data_list[i]['close'])
                self.buy_signal_date.append(data_list[i]['date'])
            elif self.has_sell_signal(data_list, i):
                self.pnl_tracker.sell(data_list[i]['close'])
        self.dense_flag = self.is_move_avg_dense(data_list, -1)
        self.is_last_price_over_threshold = data_list[-1]['close'] > self.price_threshold
        self.is_last_price_over_short_ma_avg = self.is_close_price_over_short_avg(data_list, -1)

    def is_close_price_over_short_avg(self, data, index):
        #if data[index]['MA'+str(self.short_period)] != -1 and \
        #    data[index]['close'] > data[index]['MA'+str(self.short_period)]:
        #    return True
        if data[index]['MA'+str(self.short_period)] != -1 and \
            data[index]['volume'] != 0 and \
            data[index]['PREV_MA'+str(self.short_period)] != -1 and \
            data[index]['MA_DIFF'+str(self.short_period)] > 0 and \
            data[index]['low'] >= data[index]['MA'+str(self.short_period)] and \
            data[index]['close'] >= self.price_threshold:
            return True
        return False

    # 主要买信号函数
    def has_buy_signal(self, data, index):
        # 均线破线并且拐头
        if data[index]['MA'+str(self.short_period)] != -1 and \
           data[index]['PREV_MA'+str(self.short_period)] != -1 and \
           data[index]['MA_DIFF'+str(self.short_period)] > 0 and \
           data[index-1]['MA_DIFF'+str(self.short_period)] < 0 and \
           data[index]['close'] > data[index]['MA'+str(self.short_period)]:
           # self.is_move_avg_dense(data, index):
           return True

        # 均线向上，并且最低价大于均线
        if data[index]['MA'+str(self.short_period)] != -1 and \
            data[index]['volume'] != 0 and \
            data[index]['PREV_MA'+str(self.short_period)] != -1 and \
            data[index]['MA_DIFF'+str(self.short_period)] > 0 and \
            data[index]['low'] >= data[index]['MA'+str(self.short_period)]:
            return True
        return False

    # 主要卖信号函数
    def has_sell_signal(self, data, index):
        # 止损线
        if self.pnl_tracker.avg_cost == 0:
            return False
        if ((self.pnl_tracker.avg_cost - data[index]['close']) / self.pnl_tracker.avg_cost > self.loss_threshold) or data[index]['close'] < data[index]['MA'+str(self.short_period)]:
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
        # print('total points is : {}'.format(total_count))
        # print('final win rate is : {}'.format(self.win_count / total_count))
        # print('final loss rate is : {}'.format(self.loss_count / total_count))
        # print('max profit : {}'.format(self.max_percent_profit))
        # print('max loss : {}'.format(self.max_percent_loss))
        result_dict = {
            'StockCode' : self.stock_code,
            'Total_count' : self.pnl_tracker.total_trade_count,
            'MaxProfit' : self.pnl_tracker.max_profit,
            'MaxLoss' : self.pnl_tracker.max_loss,
            'TotalProfitMoney' : self.pnl_tracker.total_profit_money,
            'TotalLossMoney' : self.pnl_tracker.total_loss_money,
            'FinalMoneyCompare' : self.pnl_tracker.current_assets + self.pnl_tracker.current_pos_value - self.pnl_tracker.start_money,
            'IsCloseOverShortMaAvg' : self.is_last_price_over_short_ma_avg,
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
                raise
                continue
            data_list.append(statistic_instance.gen_final_result())
            i += 1
        if dump_csv:
            df = pd.DataFrame(data_list)
            date_str = datetime.now().strftime('%Y/%m/%d')
            dump_dir = os.path.join(dump_file_base_dir, date_str)
            sub.check_call('mkdir -p {}'.format(dump_dir), shell=True)
            df_file = os.path.join(dump_dir, 'ma_statistic_result.csv')
            df.to_csv(df_file, index=False)
        print('*' * 100)
        for item in failed_stock:
            print(item)
        print('*' * 100)
    else:
        stock_code += '.XSHE' if stock_code.startswith('00') else '.XSHG'
        statistic_instance = SingleStockMaStatistic(stock_code)
        statistic_instance.run_ma_break_statistic()
        for date in statistic_instance.buy_signal_date:
            print(date)
        print('profit, loss, assets, pos_value, fee')
        print(
            statistic_instance.pnl_tracker.total_profit_money,
            statistic_instance.pnl_tracker.total_loss_money,
            statistic_instance.pnl_tracker.current_assets,
            statistic_instance.pnl_tracker.current_pos_value,
            statistic_instance.pnl_tracker.total_fee,
        )

def compare_with_yest():
    today_str = datetime.now().strftime('%Y-%m-%d')
    yest_date_str = self.trading_date_helpler.get_prev_trading_date(today_str).replace('-', '/')
    yest_date_path = os.path.join(dump_file_base_dir, yest_date_str, self.dump_file_name)
    yest_df = pd.read_csv(yest_date_path, usecol=['StockCode', 'CheckFlag'])
    yest_need_check_df = yest_df[yest_df['CheckFlag'] == True].rename(columns={'CheckFlag' : 'YestCheckFlag'})

    today_date_path = os.path.join(dump_file_base_dir, today_str, self.dump_file_name)
    today_df = pd.read_csv(today_date_path, usecol=['StockCode', 'CheckFlag'])
    today_need_check_df = today_df[today_df['CheckFlag'] == True].rename(columns={'CheckFlag' : 'TodayCheckFlag'})

    compare_df = yest_need_check_df.merge(today_need_check_df, on=['StockCode'], how='outer').fillna(False)

    today_date_path = os.path.join(dump_file_base_dir, today_str, self.diff_file_name)
    compare_df.to_csv(today_date_path, index=False)

if __name__ == '__main__':
    argh.dispatch_commands([run, compare_with_yest])
