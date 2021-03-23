class PnlTracker():
    def __init__(self, start_money):
        self.start_money = start_money
        self.current_assets = start_money
        self.prev_assets = start_money
        self.current_pos_value = 0
        self.pnl = 0
        self.position = 0
        self.trade_fee_rate = 0.0007
        self.total_fee = 0
        self.total_trade_count = 0
        self.total_loss = 0
        self.total_loss_money = 0
        self.max_lose = 0
        self.avg_cost = 0

    def buy(self, price, volume):
        volume = self.control_position(price)
        if volume % 100 != 0:
            return -1
        need_money = price * volume
        fee = need_money * self.trade_fee_rate
        if need_money + fee > self.current_assets:
            return -1
        if self.position == 0:
            self.prev_assets = self.current_assets
        self.current_assets -= (need_money + fee)
        self.current_pos_value += need_money
        self.position += volume
        self.total_fee += fee
        if self.position > 0:
            self.avg_cost = self.current_pos_value / self.position
        #print(self.current_pos_value, self.position, self.avg_cost)

    def sell(self, price, volume):
        volume = self.position
        if volume % 100 != 0:
            return -1
        if self.position < volume:
            return -1

        sell_money = price * volume
        fee = sell_money * self.trade_fee_rate
        self.current_assets += (sell_money - fee)
        self.position -= volume
        self.total_fee += fee
        self.total_trade_count += 1
        self.current_pos_value = self.current_pos_value - sell_money if self.position != 0 else 0
        self.avg_cost = self.current_pos_value / self.position if self.position != 0 else 0
        if self.prev_assets > self.current_assets:
            self.total_loss += 1
            self.total_loss_money += (self.prev_assets - self.current_assets)
            self.max_lose = self.max_lose if self.max_lose > (self.prev_assets - self.current_assets) else (self.prev_assets - self.current_assets)
            return self.prev_assets - self.current_assets
        return 0

    def control_position(self, price):
        usable_money = self.current_assets * 0.4
        can_buy = int(usable_money / price)
        return can_buy - can_buy % 100
