from get_data_base import *
from jqdatasdk import *

QUERY_COUNT_THRESHOLD = 1000

class JQDataExtractor(DataExtractorBase):
    def __init__(self):
        super().__init__()
        auth('18574617263', 'yhgtakdh11')

    def __is_query_enough(self):
        count = get_query_count()
        return QUERY_COUNT_THRESHOLD < count['spare']

    def get_kline_data(self, stock_code, start_date, end_date, freq):
        if not self.__is_query_enough():
            return False, []
        return True, get_price(stock_code, start_date, end_date, freq, fields=None, skip_paused=False, fq=None)

    def get_cur_data(self):
        if not self.__is_query_enough():
            return False, []
        return True, get_current_data()

    def get_all_stock(self):
        if not self.__is_query_enough():
            return False, []
        return True, list(get_all_securities(['stock']).index)

    def get_daily_query_quote(self):
        count = get_query_count()
        return count['spare']
