#include <string>

class BaseStrategy {
public:
    BaseStrategy() {}
    ~BaseStrategy() {}
    virtual void load_history_data() = 0;
    virtual inline bool has_buy_signal(close, date);
    virtual inline bool has_sell_signal(close, date);
    virtual inline bool realtime_has_buy_signal(close);
    virtual inline bool realtime_has_sell_signal(close);
    virtual void init(std::string peroid);
}
