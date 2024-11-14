from pandas import interval_range

from backtest import *
import yfinance as yf

class BuyAndSellSwitch(Strategy):
    def on_bar(self):
        if self.position_size == 0:
            limit_price = self.close * 0.995
            self.buy_limit('AAPL', size = 100, limit_price = limit_price)
            print(self.current_idx, "buy")
        else:
            limit_price = self.close * 1.005
            self.sell_limit('AAPL', size = 100, limit_price = limit_price)
            print(self.current_idx, "sell")



data = yf.Ticker('AAPL').history(start = "2022-12-01", end = "2022-12-31", interval = "1d")
e = Engine()
e.add_data(data)
e.add_strategy(BuyAndSellSwitch())
e.run()

print(e._get_stats())
print(e.strategy.trades)