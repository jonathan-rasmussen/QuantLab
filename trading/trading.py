from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import TickerId
import threading
import time
import pandas as pd
from techAnalysis import TechnicalAnalysis
from orderManager import OrderManager
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read("config.txt")

# Access values
host = config["CONNECTION"]["HOST"]
port = int(config["CONNECTION"]["PORT"])
client_id = int(config["CONNECTION"]["ID"])

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

class IBConnection(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, wrapper = self)
        self.data = {}
        self.data_ready = False
        self.next_order_id = None

    def connect(self, host, port, client_id):
        super().connect(host, port, client_id)

        # IBKR api is asynchronous, run threading to maintain connection
        thread = threading.Thread(target = self.run)
        thread.start()
        time.sleep(1)

    def nextValidId(self, orderID: TickerId):
        super().nextValidId(orderID)
        self.next_order_id = orderID
        return self.next_order_id

    def historicalData(self, reqID, bar):
        if reqID not in self.data:
            self.data[reqID] = []

        self.data[reqID].append({
            "date" : bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        })

    def historicalDataEnd(self, reqID, start, end):
        self.data_ready = True

    def requestData(self, symbol, duration, bar_size, sec_type, exchange, currency, uniqueReqID):

       # Init IBKR Contract class
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = currency

        # request historical data
        self.reqHistoricalData(
            reqId = uniqueReqID,
            contract = contract,
            endDateTime = "", # Empty string is most recent
            durationStr = duration,
            barSizeSetting = bar_size,
            whatToShow = "TRADES",
            useRTH = 0,
            formatDate = 1, # default option
            keepUpToDate= True, # Update as we go
            chartOptions= [] # no extra options
        )


    def newCandle(self, new_bar):
        print(f'New Data Recieved. Latest bar: {new_bar}')
        ta = TechnicalAnalysis()
        om = OrderManager(self)

        buy_contract = om.create_contract("SPY")
        order = om.create_bracket_order("BUY", 1, 400, 401, 399)

        for specific_order in order:
            om.place_order(buy_contract, specific_order)

        if (ta.hammer_detect(new_bar)):
            print('Hammer detected. Placing order')
            buy_contract = om.create_contract("SPY")
            order = om.create_bracket_order("BUY", 1, 400, 401, 399)
            # order = om.create_limit_order("BUY", 1, 400)
            # om.place_order(buy_contract, order)
            # order = om.create_bracket_order("BUY", 1, new_bar['Close'], new_bar["close"] + 0.4, new_bar["close"] - 0.4)

            for specific_order in order:
                om.place_order(buy_contract, specific_order)


def main():
    IBConnect = IBConnection()
    IBConnect.connect(host, port, client_id)

    # Recieve delayed market data due to none-subscription
    IBConnect.reqMarketDataType(3)

    # request market data of ticker on 1D interval with 1 min frequency

    uniqueReqID = 1
    while True:
        IBConnect.requestData("SPY", "1 D", "1 Min",
                              "STK", "SMART", "USD", uniqueReqID)
        while not(IBConnect.data_ready):
            time.sleep(1)


        IBConnect.newCandle(IBConnect.data[uniqueReqID][-1])
        # hammer_result = ta.hammer_detect(IBConnect.data[uniqueReqID][-1])
        # print(hammer_result)
        df = pd.DataFrame(IBConnect.data)
        # print(df)
        IBConnect.data = {}
        IBConnect.data_ready = False
        uniqueReqID += 1
        time.sleep(60) # change this based on candle length i.e 1 Min == 60 seconds


if __name__ == "__main__":
    main()