#ifndef __K_LINE_SIMPLE_STRATEGY_H
#define __K_LINE_SIMPLE_STRATEGY_H

#include <iostream>
#include "csv_reader.h"
#include <string>

class KLineSimpleStrategy {
public:
    KLineSimpleStrategy(std::string stk_code, std::string peroid="daily", int ema_quick_peroid=12, int ema_slow_peroid=26, int dea_peroid=9) : stock_code(stk_code) {
        this->ema_quick_alpha = 2.0 / (ema_quick_peroid + 1);
        this->ema_slow_alpha = 2.0 / (ema_slow_peroid + 1);
        this->dea_alpha = 2.0 / (dea_peroid + 1);
        init(peroid);
    }
    ~KLineSimpleStrategy();
    void load_history_data();
    void regression_test();
private:
    void init(std::string peroid);
    inline bool has_buy_signal();
    inline bool has_sell_signal();
    inline double calc_ema(double close, double current, double alpha);
    void update_self_ema(double close);
    void update_self_dea(double diff);

    CsvReader* csv_reader;
    std::string stock_code;
    std::string cur_date;

    int ema_quick_peroid;
    int ema_slow_peroid;
    int dea_peroid;

    double ema_quick_alpha = 0.0;
    double ema_quick_prev = 0.0;
    double ema_quick_current = 0.0;

    double ema_slow_alpha = 0.0;
    double ema_slow_prev = 0.0;
    double ema_slow_current = 0.0;

    double dea_alpha = 0.0;
    double dea_prev = 0.0;
    double dea_current = 0.0;
    bool is_first_calc = true;
};
#endif
