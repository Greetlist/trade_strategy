import argh
import copy
from _daily_k_line_simple_strategy import *

def run_strategy(strategy, start_money, trade_volume=100):
    selected_stratety = DailyKLineSimpleStrategy(start_money, trade_volume, '000001.XSHE')
    selected_stratety.run()

if __name__ == '__main__':
    argh.dispatch_command(run_strategy)
