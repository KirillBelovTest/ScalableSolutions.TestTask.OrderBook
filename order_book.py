from enum import Enum


class NoOrderEx(Exception):

    def __init__(self, order_id: int):
        super().__init__("In the order book doesn't exists order with id = {}".format(order_id))


class BadOrderEx(Exception):

    def __init__(self, order, key, val):
        super().__init__("Incorrect {} = {} in {}".format(key, val, order))


class DubOrderEx(Exception):

    def __init__(self, id):
        super().__init__("In the order book already exists order with id = {}".format(id))


class Side(Enum):
    BUY = 0
    SELL = 1


class State(Enum):
    NONE = 0
    OPENED = 1
    CANCELED = 2


class Order:

    def __init__(self, side: Side, price: float, quantity: float):
        self.side = side
        self.price = price
        self.quantity = quantity

        self.state = State.NONE
        self.id = ""

    @staticmethod
    def _is_val(n):
        """Check that 'n' is number value greater than 0.
        """
        return (type(n) == int or type(n) == float) and n > 0

    def make_id(self):
        self.id = "{}-{}-{}".format(self.side.value, self.price, self.__hash__())

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
        if not isinstance(self.id, str):
            raise BadOrderEx(self, "id", self.id)
        if not Order._is_val(self.price):
            raise BadOrderEx(self, "price", self.price)
        if not Order._is_val(self.quantity):
            raise BadOrderEx(self, "quantity", self.quantity)

        return self

    def __eq__(self, order) -> bool:
        if isinstance(order, Order):
            return self.id == order.id and self.price == order.price and self.quantity == order.quantity and self.side == order.side and self.state == order.state
        else:
            return NotImplemented

    def __str__(self) -> str:
        return "Order(side = {}, price = {}, quantity = {}, state = {}, id = {})".format(self.side, self.price,
                                                                                         self.quantity, self.state,
                                                                                         self.id)


class OrderBook:

    def __init__(self):
        self.orders = {Side.BUY: {}, Side.SELL: {}}

    def add_order(self, order: Order) -> str:
        """Add object with type Order to internal dict.
        Generate order id and set this value to the field of the order named 'id'. 
        Returns unique generated order id.
        If order with the same id exists in the order book then raise exception. 
        """
        if order.state is State.NONE:
            copy = order.copy()
            copy.state = State.OPENED
            copy.make_id()
            copy.check()
            if not copy.price in self.orders[copy.side]:
                self.orders[copy.side][copy.price] = {}
            self.orders[copy.side][copy.price][copy.id] = copy
            return copy.id
        else:
            raise BadOrderEx(order, "(id or state)", (order.id, order.state))

    def get_order(self, order_id: str) -> Order:
        """Get order from internal dict by id.
        Returns order with passed id or raise exception if this order doesn't exists.
        """
        side, price = order_id.split("-")[0]
        if order_id in self.orders:
            return self.orders[order_id].copy()
        else:
            raise NoOrderEx(order_id)

    def del_order(self, order_id: int) -> Order:
        """Delete order from order book.
        Returns order with passed id or raise exception if this order doesn't exists. 
        Change order state to 'canceled'.
        """
        if order_id in self.orders:
            order = self.orders.pop(order_id)
            order.state = State.CANCELED
            return order
        else:
            raise NoOrderEx(order_id)

    @property
    def market_data(self) -> dict:
        """Returns representation of all orders as a dictionary with keys 'asks' and 'bids'. 
        """
        def aggr_orders(side: Side) -> list:
            """Local func that returns filtered and aggregated list of orders.
            """
            orders = filter(lambda o: o.side is side, list(self.orders.values()))
            orders = list(map(lambda o: {"price": o.price, "quantity": o.quantity}, orders))
            orders.sort(key=lambda o: o.price, reverse=True)
            if len(orders) > 1:
                for i in range(len(orders) - 1):
                    if orders[i]["price"] == orders[i + 1]["price"]:
                        orders[i + 1]["quantity"] = orders[i + 1]["quantity"] + orders[i]["quantity"]
                        orders[i]["quantity"] = 0
            return list(filter(lambda d: d["quantity"] > 0, orders))

        return {"asks": aggr_orders(Side.SELL), "bids": aggr_orders(Side.Buy)}

