class PnlTracker():
    def __init__(self, start_money):
        self.start_money = start_money
        self.current_pos_value = start_money
        self.pnl = 0
        self.position = 0
        self.trade_fee_rate = 0.0007

    def buy(self, price, volume):
        if volume % 100 != 0:
            return -1
        need_money = price * volume
        fee = need_money * self.trade_fee_rate
        if need_money > self.current_pos_value:
            return -1
        self.current_pos_value -= (need_money + fee)
        self.position += volume

    def sell(self, price, volume):
        if volume % 100 != 0:
            return -1
        if self.position < volume:
            return -1
        sell_money = price * volume
        fee = sell_money * self.trade_fee_rate
        self.current_pos_value += (sell_money - fee)
        self.position -= volume
