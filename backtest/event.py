class Event(object):
    """
    Base class to be inherited by event classes
    """
    pass

class MarketEvent(Event):
    """
    Handles  the event of new market bar data update
    """

    def __init__(self):
        self.type = "MARKET"


class SignalEvent(Event):
    """
    Handles event of sending a signal from Strategy object.
    This is recieved by a Portfolio object.
    """

    def __init__(self, symbol, datetime, signal_type):
        """
        :param symbol: Ticker Symbol
        :param datetime: Timestamp at which signal was generated
        :param signal_type: "LONG" or "SHORT" direction
        """

        self.type = "SIGNAL"
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type

class OrderEvent(Event):
    """
    Handles the event of sending an Order to execution.
    """

    def __init__(self, symbol, order_type, quantity, direction):
        """
        :param symbol: Ticker to be traded
        :param order_type: "MKT" (market) or "LMT" (limit)
        :param quantity: Positive integer for quantity
        :param direction: "BUY" (long) or "SELL" (short)
        """

        self.type = "ORDER"
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        """
        Output to console values within Order
        :return:
        """
        print(f"Order: Symbol={self.symbol}, Type={self.order_type}, Quantity={self.quantity}, Direction= {self.direction}")


class FillEvent(Event):
    """
    Event of a simulated Filled Order as from brokerage.
    Stores the quantity of actual fill, price and commission.
    """

    def __init__(self, timeindex, symbol, exchange, quantity, direction, fill_cost, commission = None):
        """
        :param timeindex: bar resolution for fufilled order
        :param symbol: instrument of fill
        :param exchange: exchange of fill
        :param quantity: filled quantity
        :param direction: direction of fill ("BUY" or "SELL")
        :param fill_cost: value in dollars
        :param commission: Optional commission fee
        """

        self.type = "FILL"
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        if commission is None:
            self.commission = self.calculate_commission()
        else:
            self.commission = commission

    def calculate_commission(self):
        """
        Calculate trading fees based on IBs fee strutuce for API (USD)
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2

        :return:
        """
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else: # Quantity greater then 500
            full_cost = max(1.3, 0.008 * self.quantity)
        full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
        return full_cost