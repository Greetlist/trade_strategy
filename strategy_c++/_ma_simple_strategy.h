#ifndef __MA_SIMPLE_STRATEGY_H
#define __MA_SIMPLE_STRATEGY_H
class MaSimpleStrategy : public BaseStrategy {
public:
    MaSimpleStrategy();
    ~MaSimpleStrategy();
    void load_history_data();
    bool has_buy_signal();
    bool has_sell_signal();
    bool realtime_has_buy_signal();
    bool realtime_has_sell_signal();
    void init();
private:
    int calc_curr_ma(double price);
}

#endif
