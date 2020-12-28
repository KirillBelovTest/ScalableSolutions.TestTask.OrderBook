# %%
import uuid
from enum import Enum

# %%
class NoOrderEx(Exception):

    def __init__(self, id: int):
        super().__init__("In the order book doesn't exists order with id = {}".format(id))

# %%
class BadOrderEx(Exception):

    def __init__(self, order, key, val):
        super().__init__("Incorret {} = {} in {}".format(key, val, order))

# %%
class DubOrderEx(Exception):

    def __init__(self, id):
        super().__init__("In the order book already exists order with id = {}".format(id))

# %%
class Side(Enum):
    BUY = 0
    SELL = 1

# %%
class State(Enum):
    NONE = 0
    OPENED = 1
    CANCELED = 2

# %%
class Order:

    def __init__(self, side: Side, price: float, quantity: float):
        self.side = side
        self.price = price
        self.quantity = quantity

        self.state = State.NONE
        self.id = 0

    @staticmethod
    def _is_val(n):
        """Check that 'n' is number value greater than 0.
        """
        return (type(n) == int or type(n) == float) and n > 0

    def copy(self):
        """Copy order to new object.
        """
        order = Order(self.side, self.price, self.quantity)
        order.state = self.state
        order.id = self.id
        return order

    def check(self):
        """Returns 'self' or raise exception if one of the field is incorrect.
        """
        if not isinstance(self.side, Side):
            raise BadOrderEx(self, "side", self.side)
        if not isinstance(self.state, State):
            raise BadOrderEx(self, "state", self.state)
        if not isinstance(self.id, int):
            raise BadOrderEx(self, "id", self.id)
        if not Order._is_val(self.price):
            raise BadOrderEx(self, "price", self.price)
        if not Order._is_val(self.quantity):
            raise BadOrderEx(self, "quantity", self.quantity)
        
        return self
    
    def __eq__(self, order) -> bool:
        try:
            return self.id == order.id and self.price == order.price and self.quantity == order.quantity and self.side == order.side and self.state == order.state
        except:
            return False
    
    def __str__(self) -> str:
        return "Order(side = {}, price = {}, quantity = {}, state = {}, id = {})".format(self.side, self.price, self.quantity, self.state, self.id)

# %%
class OrderBook:

    def __init__(self):
        self.orders = {}

    def add_order(self, order: Order) -> int:
        """Add object with type Order to internal dict.
        Generate order id and set this value to the field of the order named 'id'. 
        Returns unique generated order id.
        If order with the same id exists in the order book then raise exception. 
        """
        if order.id == 0 and order.state is State.NONE:
            copy = order.copy()
            copy.state = State.OPENED
            copy.id = uuid.uuid4().int
            self.orders[copy.id] = copy.check()
            return copy.id
        else:
            raise BadOrderEx(order, "(id or state)", (order.id, order.state))

    def get_order(self, id: int) -> Order:
        """Get order from internal dict by id.
        Returns order with passed id or raise exception if this order doesn't exists.
        """
        if id in self.orders:
            return self.orders[id].copy()
        else:
            raise NoOrderEx(id)

    def del_order(self, id: int) -> Order: 
        """Delete ordere from order book.
        Returns order with passed id or raise exception if this order doesn't exists. 
        Change order state to 'canceled'.
        """
        if id in self.orders:
            order = self.orders.pop(id)
            order.state = State.CANCELED
            return order
        else:
            raise NoOrderEx(id)

    def market_data(self) -> dict:
        """Returns representation of all orders as a dictionary with keys 'asks' and 'bids'. 
        """
        orders = list(self.orders.values())
        orders.sort(key = lambda o: o.price, reverse = True)

        asks = filter(lambda o: o.side is Side.SELL, orders)
        asks = list(map(lambda o: { "price": o.price, "quantity": o.quantity }, asks))
        if len(asks) > 1:
            for i in range(len(asks) - 1):
                if asks[i]["price"] == asks[i + 1]["price"]:
                    asks[i + 1]["quantity"] = asks[i + 1]["quantity"] + asks[i]["quantity"]
                    asks[i]["quantity"] = 0
        asks = list(filter(lambda d: d["quantity"] > 0, asks))

        bids = filter(lambda o: o.side is Side.BUY, orders)
        bids = list(map(lambda o: { "price": o.price, "quantity": o.quantity }, bids))
        if len(bids) > 1:
            for i in range(len(bids) - 1):
                if bids[i]["price"] == bids[i + 1]["price"]:
                    bids[i + 1]["quantity"] = bids[i + 1]["quantity"] + bids[i]["quantity"]
                    bids[i]["quantity"] = 0
        bids = list(filter(lambda d: d["quantity"] > 0, bids))

        return { "asks": asks, "bids": bids }

