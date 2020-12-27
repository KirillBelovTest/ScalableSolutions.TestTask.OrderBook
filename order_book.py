# %%
class Order:

    def __init__(self, side: str, price: float, quantity: float):
        self.side = side
        self.price = price
        self.quantity = quantity

        self.state = None
        self.id = self.__hash__()

    @staticmethod
    def _is_val(n):
        """Check that 'n' is number value greater than 0.
        """
        return (type(n) == int or type(n) == float) and n > 0

    def check(self):
        """Returns 'self' or raise exception if one of the field is incorrect.
        """
        if self.side != "sell" and self.side != "buy":
            raise Exception("Incorrect 'side' = '{1}' in {0}".format(self, self.side))
        if self.state != None and self.state != "canceled" and self.state != "opened":
            raise Exception("Incorrect 'state' = '{1}' in {0}".format(self, self.state))
        if type(self.id) != int:
            raise Exception("Incorrect 'id' = '{1}' in {0}".format(self, self.id))
        if not Order._is_val(self.price):
            raise Exception("Incorrect 'price' = '{1}' in {0}".format(self, self.price))
        if not Order._is_val(self.quantity):
            raise Exception("Incorrect 'quantity' = '{1}' in {0}".format(self, self.quantity))
        
        return self


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
        if not order.id in self.orders and order.state == None:
            order.state = "opened"
            self.orders[order.id] = order.check()
            return order.id
        else:
            raise Exception("Order with '{}' already in the order book".format(order.id))

    def get_order(self, id: int) -> Order:
        """Get order from internal dict by id.
        Returns order with passed id or raise exception if this order doesn't exists.
        """
        return self.orders[id]

    def del_order(self, id: int) -> Order: 
        """Delete ordere from order book.
        Returns order with passed id or raise exception if this order doesn't exists. 
        Change order state to 'canceled'.
        """
        order = self.orders.pop(id)
        order.state = "canceled"
        return order

    def market_data(self) -> dict:
        """Returns representation of all orders as a dictionary with keys 'asks' and 'bids'. 
        """
        orders = list(self.orders.values())
        orders.sort(key = lambda o: o.price, reverse = True)

        asks = filter(lambda o: o.side == "sell", orders)
        asks = list(map(lambda o: { "price": o.price, "quantity": o.quantity }, asks))
        if len(asks) > 1:
            for i in range(len(asks) - 1):
                if asks[i]["price"] == asks[i + 1]["price"]:
                    asks[i + 1]["quantity"] = asks[i + 1]["quantity"] + asks[i]["quantity"]
                    asks[i]["quantity"] = 0
        asks = list(filter(lambda d: d["quantity"] > 0, asks))

        bids = filter(lambda o: o.side == "buy", orders)
        bids = list(map(lambda o: { "price": o.price, "quantity": o.quantity }, bids))
        if len(bids) > 1:
            for i in range(len(bids) - 1):
                if bids[i]["price"] == bids[i + 1]["price"]:
                    bids[i + 1]["quantity"] = bids[i + 1]["quantity"] + bids[i]["quantity"]
                    bids[i]["quantity"] = 0
        bids = list(filter(lambda d: d["quantity"] > 0, bids))

        return { "asks": asks, "bids": bids }

