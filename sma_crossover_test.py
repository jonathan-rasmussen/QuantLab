import yfinance as yf
from backtest import *

class SMACrossover(Strategy):
    def on_bar(self):
        if self.position_size == 0:
            if self.data.loc[self.current_idx].sma_12 > self.data.loc[self.current_idx].sma_24:
                limit_price = self.close * 0.995
                order_size = self.cash / limit_price
                self.buy_limit('AAPL', size=order_size, limit_price=limit_price)
        elif self.data.loc[self.current_idx].sma_12 < self.data.loc[self.current_idx].sma_24:
            limit_price = self.close * 1.005
            self.sell_limit('AAPL', size=self.position_size, limit_price=limit_price)

data = yf.Ticker('AAPL').history(start='2010-12-01', end='2024-10-31', interval='1d')
e = Engine(initial_cash=1000)

data['sma_12'] = data.Close.rolling(12).mean()
data['sma_24'] = data.Close.rolling(24).mean()
e.add_data(data)

e.add_strategy(SMACrossover())
stats = e.run()
print(stats)
e.plot()