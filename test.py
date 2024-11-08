from pandas import interval_range

from backtest import *
import yfinance as yf

class BuyAndSellSwitch(Strategy):
    def on_bar(self):
        if self.position_size == 0:
            self.buy('AAPL', 1)
            print(self.current_idx, "buy")
        else:
            self.sell('AAPL', size = 1)
            print(self.current_idx, "sell")



data = yf.Ticker('AAPL').history(start = "2022-12-01", end = "2022-12-31", interval = "1d")
e = Engine()
e.add_data(data)
e.add_strategy(BuyAndSellSwitch())
e.run()
print(e._get_stats())