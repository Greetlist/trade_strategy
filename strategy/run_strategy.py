import argh
import copy
from _daily_k_line_simple_strategy import *

def run_strategy(strategy, start_money, trade_volume=100, data_period='daily'):
    selected_stratety = KLineSimpleStrategy(start_money, trade_volume, data_period, '000011.XSHE')
    selected_stratety.run()

if __name__ == '__main__':
    argh.dispatch_command(run_strategy)
