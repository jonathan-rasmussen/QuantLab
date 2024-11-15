import yfinance as yf
from backtest import *

class Test1(Strategy):
    def on_bar(self):
        if self.position_size == 0:
            limit_price = self.close * 0.995
            # We'll try to buy spend all our available cash!
            self.buy_limit('AAPL', size=8.319, limit_price=limit_price)


data = yf.Ticker('AAPL').history(start='2020-12-01', end='2024-10-31', interval='1d')
e = Engine(initial_cash=1000)
e.add_data(data)

e.add_strategy(Test1())
stats = e.run()
print(stats)
e.plot()