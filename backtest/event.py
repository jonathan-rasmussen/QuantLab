class Event(object):
    """
    Base class for subsequent events
    """
    pass

class MarketEvent(Event):
    """
    Handles  the event of new market bar data update
    """

    def __init__(self):
        self.type = "MARKET"