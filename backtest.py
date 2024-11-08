import pandas as pd
from tqdm import tqdm


class Engine():
    """The engine is the main object that will be used to run our backtest.
    """

    def __init__(self, initial_cash = 100_000):
        self.strategy = None
        self.data = None
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.current_idx = None

    def add_data(self, data):
        # add ticker OHLC data to engine
        self.data = data

    def add_strategy(self, strategy):
        # add strategy to test in engine
        self.strategy = strategy

    def run(self):

        # map data to strategy
        self.strategy.data = self.data

        for idx in tqdm(self.data.index):

            self.current_idx = idx
            self.strategy.current_idx = self.current_idx

            # Fill orders from previous run
            self._fill_orders()

            # Run strategy on current bar
            self.strategy.on_bar()
            print(idx)

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
            can_fill = False
            order_price = self.data.loc[self.current_idx]['Open']
            order_value = order_price * order.size

            # Ensure cash balance greater than order for buy
            if order.side == 'buy' and self.cash >= order_value:
                can_fill = True

            # Ensure position greater than order for sell
            elif order.side == 'sell' and self.strategy.position_size >= order.size:
                can_fill = True

            if can_fill:
                trade = Trade(
                    ticker = order.ticker,
                    side = order.side,
                    price = order_price,
                    size = order.size,
                    type = order.type,
                    idx = self.current_idx
                )
                self.strategy.trades.append(trade)
                self.cash -= trade.price * trade.size
        self.strategy.orders = []


    def _get_stats(self):
        metrics = {}
        final_portfolio_value = ((self.data.loc[self.current_idx]['Close'] * self.strategy.position_size + self.cash))
        total_return = (final_portfolio_value/ self.initial_cash - 1) * 100
        metrics['total_return'] = total_return
        return metrics



class Strategy():
    """This base class will handle the execution logic of our trading strategies
    """

    def __init__(self):
        self.current_idx = None
        self.data = None
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

    @property
    def position_size(self):
        return sum([trade.size for trade in self.trades])

    def on_bar(self):
        """
        This method is overwritten via inheritance when a specific strategy class is initialized
        """
        pass


class Trade():
    """Trade objects are created when an order is filled.
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


class Order():
    """When buying or selling, we first create an order object. If the order is filled, we create a trade object.
    """

    def __init__(self, ticker, size, side, idx):
        self.ticker = ticker
        self.side = side
        self.size = size
        self.type = "market"
        self.idx = idx