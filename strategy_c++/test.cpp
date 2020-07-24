#include "_k_line_simple_strategy.h"

using namespace std;
int main(int argc, char** argv) {
    //string file_path = "/home/greetlist/macd/data_storage/000001.XSHE/stock_60m_data/kline_60m.csv";
    //CsvReader reader(file_path);
    //std::vector<double> close_price = reader.getColumnValues<double>("close");
    //std::vector<std::string> date = reader.getColumnValues<std::string>("date");
    //int len = close_price.size();
    //for (int i = 0; i < len; ++i) {
        //cout << date[i] << " " << close_price[i] << endl;
    //}
    KLineSimpleStrategy klss("000001.XSHE", "60m");
    klss.regression_test();
    return 0;
}
