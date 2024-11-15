import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [12, 6]
import numpy as np
from tqdm import tqdm


class Engine:
    """
    The engine is the main object that will be used to run our backtest.
    """

    def __init__(self, initial_cash = 100_000):
        self.strategy = None
        self.data = None
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.cash_series = {}
        self.stock_series = {}
        self.current_idx = None
        self.trading_days = 252
        self.risk_free_rate = 0

    def add_data(self, data):
        # add ticker OHLC data to engine
        self.data = data

    def add_strategy(self, strategy):
        # add strategy to test in engine
        self.strategy = strategy

    def run(self):

        # map data to strategy
        self.strategy.data = self.data
        self.strategy.cash = self.cash


        for idx in tqdm(self.data.index):

            self.current_idx = idx
            self.strategy.current_idx = self.current_idx

            # Fill orders from previous run
            self._fill_orders()

            # Run strategy on current bar
            self.strategy.on_bar()

            # Record asset classes for AUM
            self.cash_series[idx] = self.cash
            self.stock_series[idx] = self.strategy.position_size * self.data.loc[self.current_idx]['Close']
        return self._get_stats()

    def _fill_orders(self):
        # Fill orders
        """
        this method fills buy and sell orders, creates new trade obj
        and adjusts the strategy cash balance

        Rules
        - if we buy, cash balance has to be large enough to cover the order
        - if we sell, posiiton size must be enough to cover order
        """

        for order in self.strategy.orders:

            # set fill price to open price, holds true for market orders
            fill_price = self.data.loc[self.current_idx]['Open']
            can_fill = False

            # order_price = self.data.loc[self.current_idx]['Open']
            order_value = fill_price * order.size

            # Ensure cash balance greater than order for buy
            if order.side == 'buy' and self.cash >= order_value:
                if order.type == "limit":
                    if order.limit_price >= self.data.loc[self.current_idx]['Low']:
                        fill_price = order.limit_price
                        can_fill = True

                else:
                    can_fill = True

            # Ensure position greater than order for sell
            elif order.side == 'sell' and self.strategy.position_size >= order.size:

                if order.type == "limit":
                    if order.limit_price <= self.data.loc[self.current_idx]['High']:
                        fill_price = order.limit_price
                        can_fill = True
                else:
                    can_fill = True

            if can_fill:
                trade = Trade(
                    ticker = order.ticker,
                    side = order.side,
                    price = fill_price,
                    size = order.size,
                    type = order.type,
                    idx = self.current_idx
                )
                self.strategy.trades.append(trade)
                self.cash -= trade.price * trade.size
        self.strategy.orders = []


    def _get_stats(self):

        metrics = {}

        # Total Return
        final_portfolio_value = (self.data.loc[self.current_idx]['Close'] * self.strategy.position_size + self.cash)
        total_return = (final_portfolio_value/ self.initial_cash - 1) * 100
        metrics['total_return'] = total_return

        # Buy & Hold Benchmark
        portfolio_bh_qty = self.initial_cash / self.data.loc[self.data.index[0]]['Open']
        portfolio_bh = portfolio_bh_qty * self.data.Close

        # Exposure to Asset
        portfolio = pd.DataFrame({'stock':self.stock_series,
                                  'cash':self.cash_series})
        portfolio['total_aum'] = portfolio['stock'] + portfolio['cash']
        metrics['exposure_pct'] = ((portfolio['stock'] / portfolio['total_aum']) * 100).mean()

        # Annualized Returns
        p = portfolio.total_aum
        metrics['returns_annualized'] = ((p.iloc[-1] / p.iloc[0]) ** (1 / ((p.index[-1] - p.index[0]).days / 365)) - 1) * 100

        p_bh = portfolio_bh
        metrics['returns_bh_annualized'] = ((p_bh.iloc[-1] / p_bh.iloc[0]) ** (1 / ((p_bh.index[-1] - p_bh.index[0]).days / 365)) - 1) * 100

        # Annualized Volatility
        metrics['volatility_ann'] = p.pct_change().std() * np.sqrt(self.trading_days) * 100
        metrics['volatility_bh_ann'] = p_bh.pct_change().std() * np.sqrt(self.trading_days) * 100

        # Sharpe Ratio
        metrics['sharpe_ratio'] = (metrics['returns_annualized'] - self.risk_free_rate) / metrics['volatility_ann']
        metrics['sharpe_ratio_bh'] = (metrics['returns_bh_annualized'] - self.risk_free_rate) / metrics['volatility_bh_ann']


        # Save for plotting
        self.portfolio = portfolio
        self.portfolio_bh = portfolio_bh

        # Max Drawdown
        metrics['max_drawdown'] = self.get_max_drawdown(portfolio.total_aum)
        metrics['max_drawdown_bh'] = self.get_max_drawdown(portfolio_bh)

        return metrics

    def get_max_drawdown(self, close):
        roll_max = close.cummax()
        daily_drawdown = close / roll_max - 1
        max_daily_drawdown = daily_drawdown.cummin()
        return max_daily_drawdown.min() * 100


    def plot(self):
        plt.plot(self.portfolio["total_aum"], label = "Strategy")
        plt.plot(self.portfolio_bh, label = "Buy & Hold")
        plt.legend()
        plt.show()



class Strategy:
    """
    This base class will handle the execution logic of the strategies
    """

    def __init__(self):
        self.current_idx = None
        self.data = None
        self.cash = None
        self.orders = []
        self.trades = []

    def buy(self, ticker, size = 1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'buy',
                size = size,
                idx = self.current_idx
            )
        )

    def sell(self, ticker, size = 1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'sell',
                size = -size,
                idx = self.current_idx
            )
        )


    def buy_limit(self, ticker, limit_price, size = 1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'buy',
                limit_price = limit_price,
                size = size,
                order_type = 'limit',
                idx = self.current_idx
            )
        )

    def sell_limit(self, ticker, limit_price, size = 1):
        self.orders.append(
            Order(
                ticker = ticker,
                side = 'sell',
                limit_price = limit_price,
                size = -size,
                order_type = 'limit',
                idx = self.current_idx
            )
        )

    @property
    def position_size(self):
        return sum([trade.size for trade in self.trades])

    @property
    def close(self):
        return self.data.loc[self.current_idx]['Close']

    def on_bar(self):
        """
        This method is overwritten via inheritance when a specific strategy class is initialized
        """
        pass


class Trade:
    """
    Trade objects are created when an order is filled.
    """

    def __init__(self, ticker, side, size, price, type, idx):
        self.ticker = ticker
        self.side = side
        self.price = price
        self.size = size
        self.type = type
        self.idx = idx

    def __repr__(self):
        return f'<Trade: {self.idx} {self.ticker} {self.side} {self.size}@{self.price}>'


class Order:
    """
    When buying or selling, create an order object. If the order is filled, create a trade object.
    """

    def __init__(self, ticker, size, side, idx, limit_price = None, order_type = "market"):
        self.ticker = ticker
        self.side = side
        self.size = size
        self.limit_price = limit_price
        self.type = order_type
        self.idx = idx