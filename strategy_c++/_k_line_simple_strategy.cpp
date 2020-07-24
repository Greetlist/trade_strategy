#include "_k_line_simple_strategy.h"

KLineSimpleStrategy::~KLineSimpleStrategy() {
    delete this->csv_reader;
}

void KLineSimpleStrategy::init(std::string peroid) {
    std::string file_path = \
        peroid == "daily" ? \
        std::string("/home/greetlist/macd/data_storage/" + this->stock_code + "/stock_daily_data/kline_daily.csv") :
        std::string("/home/greetlist/macd/data_storage/" + this->stock_code + "/stock_60m_data/kline_60m.csv");
    this->csv_reader = new CsvReader(file_path);
}

void KLineSimpleStrategy::load_history_data() {
    std::vector<std::string> date = this->csv_reader->getColumnValues<std::string>("date");
    std::vector<double> close = this->csv_reader->getColumnValues<double>("close");

    int data_len = date.size();
    for (int i = 0; i < data_len; ++i) {
        update_self_ema(close[i]);
        double cur_diff = this->ema_quick_current - this->ema_slow_current;
        update_self_dea(cur_diff);
        this->cur_date = date[i];
    }
}

inline double KLineSimpleStrategy::calc_ema(double close, double current, double alpha) {
    return alpha * close + (1.0 - alpha) * current;
}

void KLineSimpleStrategy::update_self_ema(double close) {
    if (this->is_first_calc) {
        this->ema_quick_current = close;
        this->ema_slow_current = close;
        this->is_first_calc = false;
    } else {
        this->ema_quick_prev = this->ema_quick_current;
        this->ema_slow_prev = this->ema_slow_current;
        this->ema_quick_current = calc_ema(close, this->ema_quick_current, this->ema_quick_alpha);
        this->ema_slow_current = calc_ema(close, this->ema_slow_current, this->ema_slow_alpha);
    }
}

void KLineSimpleStrategy::update_self_dea(double diff) {
    this->dea_prev = this->dea_current;
    this->dea_current = calc_ema(diff, this->dea_current, this->dea_alpha);
}

inline bool KLineSimpleStrategy::has_buy_signal() {
    return this->dea_prev > (this->ema_quick_prev - this->ema_slow_prev) && this->dea_current < (this->ema_quick_current - this->ema_slow_current);
}

inline bool KLineSimpleStrategy::has_sell_signal() {
    return this->dea_prev < (this->ema_quick_prev - this->ema_slow_prev) && this->dea_current > (this->ema_quick_current - this->ema_slow_current);
}

void KLineSimpleStrategy::regression_test() {
    std::vector<std::string> date = this->csv_reader->getColumnValues<std::string>("date");
    std::vector<double> close = this->csv_reader->getColumnValues<double>("close");

    int data_len = date.size();
    for (int i = 0; i < data_len; ++i) {
        update_self_ema(close[i]);
        double cur_diff = this->ema_quick_current - this->ema_slow_current;
        update_self_dea(cur_diff);
        this->cur_date = date[i];
        if (has_buy_signal()) {
            std::cout << this->stock_code << " has buy signal, date : " << this->cur_date << std::endl;
        } else if (has_sell_signal()) {
            std::cout << this->stock_code << " has sell signal, date : " << this->cur_date << std::endl;
        }
    }
}
