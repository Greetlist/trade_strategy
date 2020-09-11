#include <string>

class BaseStrategy {
public:
    BaseStrategy() {}
    ~BaseStrategy() {}
    virtual void load_history_data() = 0;
    virtual inline bool has_buy_signal(close, date);
    virtual inline bool has_sell_signal(close, date);
    virtual void init(std::string peroid);
}
