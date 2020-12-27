# %%
class OrderBook:

    def __init__(self):
        self.orders = {}

    def add_order(self, order) -> int:
        """Add object with type Order to internal dict.
        Generate order id and set this value to the field of the order named 'id'. 
        Returns unique generated order id.
        If order with the same id exists in the order book then raise exception. 
        """
        pass

    def get_order(self, id: int):
        """Get order from internal dict by id.
        Returns order with passed id or raise exception if this order doesn't exists.
        """
        pass

    def del_order(self, id: int): 
        """Delete ordere from order book.
        Returns order with passed id or raise exception if this order doesn't exists. 
        Change order state to 'canceled'
        """
        pass

    def market_data(self) -> dict:
        """Returns representation of all orders as a dictionary with keys 'asks' and 'bids'. 
        """
        pass
