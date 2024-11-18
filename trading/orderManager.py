from ibapi.order import Order
from ibapi.contract import Contract
from sympy.physics.secondquant import contraction


class OrderManager:

    def __init__(self, client):
        self.client = client

    def create_contract(self, symbol, sec_type = "STK", exchange = "SMART", currency = "USD"):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = currency
        return contract

    def create_limit_order(self, action, quantity, price):
        order = Order()
        order.action = action
        order.totalQuantity = quantity
        order.orderType = "LMT"
        order.lmtPrice = price

        order.orderId = self.client.next_order_id
        self.client.next_order_id += 1
        return order

    def place_order(self, contract, order):
        self.client.placeOrder(order.orderId, contract, order)


    def create_bracket_order(self, action, quantity, entry_price, take_profit_price, stop_loss_price):

        entry_order = self.create_limit_order("BUY", quantity, entry_price)
        parent_id = entry_order.orderId
        entry_order.transmit = False

        take_profit_order = self.create_limit_order("SELL", quantity, take_profit_price)
        take_profit_order.parentId = parent_id
        take_profit_order.transmit = False

        stop_loss_order = Order()
        stop_loss_order.action = action
        stop_loss_order.totalQuantity = quantity
        stop_loss_order.orderType = "STP"
        stop_loss_order.auxPrice = stop_loss_price
        stop_loss_order.parentId = parent_id
        stop_loss_order.orderId = self.client.next_order_id
        self.client.next_order_id += 1
        stop_loss_order.transmit = True

        return (entry_order, take_profit_order, stop_loss_order)



