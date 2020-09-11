class PnlTracker():
    def __init__(self, start_money):
        self.start_money = start_money
        self.current_pos_value = start_money
        self.pnl = 0
        self.position = 0
        self.trade_fee_rate = 0.0007
        self.total_fee = 0

    def buy(self, price, volume):
        volume = self.control_position(price)
        if volume % 100 != 0:
            return -1
        need_money = price * volume
        fee = need_money * self.trade_fee_rate
        if need_money > self.current_pos_value:
            return -1
        self.current_pos_value -= (need_money + fee)
        self.position += volume
        self.total_fee += fee

    def sell(self, price, volume):
        volume = self.position
        if volume % 100 != 0:
            return -1
        if self.position < volume:
            return -1
        sell_money = price * volume
        fee = sell_money * self.trade_fee_rate
        self.current_pos_value += (sell_money - fee)
        self.position -= volume
        self.total_fee += fee

    def control_position(self, price):
        usable_money = self.current_pos_value * 0.3
        can_buy = int(usable_money / price)
        return  can_buy - can_buy % 100
