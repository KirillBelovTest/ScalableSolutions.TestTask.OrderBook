import pytest
import random
from order_book import BadOrderEx
from order_book import NoOrderEx
from order_book import DubOrderEx
from order_book import Side
from order_book import State
from order_book import Order
from order_book import OrderBook

# helper funcs

def is_same_orders(order1: Order, order2: Order) -> bool:
    """Compare only order values (without id  or state).
    """
    return order1.side == order2.side and order1.price == order2.price and order1.quantity == order2.quantity

# data

def random_order() -> Order:
    """Random correct order.
    """
    random.seed()
    side = random.choice([Side.BUY, Side.SELL])
    price = random.random()
    quantity = random.random()
    return Order(side, price, quantity)

def random_buy_order() -> Order:
    """Random correct buy order.
    """
    order = random_order()
    order.side = Side.BUY
    return order

def random_sell_order() -> Order:
    """Random correct sell order.
    """
    order = random_order()
    order.side = Side.SELL
    return order

def good_orders() -> list:
    """Orders with correct parameters.
    """
    yield Order(Side.BUY, 1, 2)
    yield Order(Side.SELL, 3, 4)
    yield Order(Side.BUY, 5.6, 7.8)
    yield Order(Side.SELL, 0.0000000000000001, 2000000000000000.0)
    yield Order(Side.SELL, 3000000000000000.0, 0.0000000000000004)

def bad_orders() -> list:
    """Orders with incorrect parameters.
    """
    yield Order("foo", 1, 2)
    yield Order(Side.BUY, 0, 3)
    yield Order(Side.SELL, 4, -1)
    yield Order([], 5, 6)
    yield Order(Side.BUY, "$7", 8)
    yield Order(Side.SELL, 9, "1PC")
    yield Order(Side.BUY, 0.001, -0.01)
    yield Order(Side.SELL, -0.001, 0.01)

# success 'order book' tests

def test_succes_order_book_01_create():
    print("Create order book")
    book = OrderBook()

    print("Check order book internal fields")
    assert type(book.orders) == dict
    assert len(book.orders) == 0

# success 'add order' tests

@pytest.mark.parametrize("order", good_orders())
def test_succes_add_order_01_one_order(order):
    print("Create order book")
    book = OrderBook()

    print("Add order to order book")
    id = book.add_order(order)

    print("Check that result of adding is int value")
    assert isinstance(id, int)
    print("Check that in order book is one order")
    assert len(book.orders) == 1

    print("Extract order from internal dict")
    order_added = book.orders[id]

    print("Check that retuned result and order id is the same")
    assert id == order_added.id
    print("Check that order state is OPENED")
    assert order_added.state == State.OPENED
    print("Check that values of orders is the same")
    assert is_same_orders(order, order_added)

def test_success_add_order_02_several_orders():
    print("Create order book")
    book = OrderBook()

    print("Adding several orders")
    orders = list(good_orders())
    for order in orders:
        book.add_order(order)

    print("Check that all orders was been added")
    assert len(book.orders) == len(orders)

# success 'del order' tests

@pytest.mark.parametrize("order", good_orders())
def test_success_del_order_01_one_order(order):
    print("Create order book")
    book = OrderBook()

    print("Adding order")
    id = book.add_order(order)

    print("Check result of calling 'del_order'")
    order_deleted = book.del_order(id)

    assert is_same_orders(order, order_deleted)
    assert len(book.orders) == 0
    assert order_deleted.state == State.CANCELED

# success 'get order' tests

@pytest.mark.parametrize("order", good_orders())
def test_succes_get_order_01_one_order(order):
    print("Create order book")
    book = OrderBook()

    print("Adding order")
    id = book.add_order(order)
    
    print("Check result of calling 'get_order'")
    order_taken = book.get_order(id)

    assert order_taken.state == State.OPENED
    assert is_same_orders(order, order_taken)
    assert len(book.orders) == 1
    assert book.orders == { order_taken.id: order_taken }

# succes 'show market data' tests

def test_market_data_01_check_struct():
    print("Create order book")
    book = OrderBook()

    print("Create several orders")
    order1 = random_buy_order()
    order2 = random_sell_order()

    print("Adding several orders")
    book.add_order(order1)
    book.add_order(order2)

    print("Getting market data")
    market = book.market_data()

    assert market == { 
        "asks": [{ "price": order2.price, "quantity": order2.quantity }], 
        "bids": [{ "price": order1.price, "quantity": order1.quantity }] 
    }

def test_market_data_02_check_sorting():
    print("Create order book")
    book = OrderBook()

    print("Create several orders")
    order1 = Order(Side.BUY, 1, 1)
    order2 = Order(Side.SELL, 9, 2)
    order3 = Order(Side.BUY, 3, 3)
    order4 = Order(Side.SELL, 7, 4)
    order5 = Order(Side.BUY, 2, 5)
    order6 = Order(Side.SELL, 8, 6)

    print("Adding several orders")
    book.add_order(order1)
    book.add_order(order2)
    book.add_order(order3)
    book.add_order(order4)
    book.add_order(order5)
    book.add_order(order6)
    
    print("Getting market data")
    market = book.market_data()

    assert market["asks"] == sorted(market["asks"], key = lambda d: d["price"], reverse = True)
    assert market["bids"] == sorted(market["bids"], key = lambda d: d["price"], reverse = True)

def test_market_data_03_check_agregation():
    print("Create order book")
    book = OrderBook()

    print("Create several orders")
    order1 = Order(Side.BUY, 1, 1)
    order2 = Order(Side.SELL, 2, 1)
    order3 = Order(Side.BUY, 1, 1)
    order4 = Order(Side.SELL, 2, 1)
    
    print("Adding several orders")
    book.add_order(order1)
    book.add_order(order2)
    book.add_order(order3)
    book.add_order(order4)

    print("Getting market data")
    market = book.market_data()

    assert market == { 
        "asks": [{ "price": 2.0, "quantity": 2.0 }], 
        "bids": [{ "price": 1.0, "quantity": 2.0 }] 
    }

# success 'try to change order in order book'

def test_except_try_change_01_side_after_add():
    print("Create order book")
    book = OrderBook()

    print("Create simple order")
    order = Order(Side.BUY, 1, 1)

    print("Adding order")
    id = book.add_order(order)

    print("Trying to change order from outside")
    order.side = "foo"
    order_added = book.get_order(id)

    assert not is_same_orders(order, order_added)

def test_except_try_change_02_price_after_add():
    print("Create order book")
    book = OrderBook()

    print("Create simple order")
    order = Order(Side.BUY, 1, 1)

    print("Adding order")
    id = book.add_order(order)

    print("Trying to change order from outside")
    order.price = -1
    order_added = book.get_order(id)

    assert not is_same_orders(order, order_added)

def test_except_try_change_03_quantity_after_add():
    print("Create order book")
    book = OrderBook()

    print("Create simple order")
    order = Order(Side.BUY, 1, 1)

    print("Adding order")
    id = book.add_order(order)

    print("Trying to change order from outside")
    order.quantity = -1
    order_added = book.get_order(id)

    assert not is_same_orders(order, order_added)

# excepr 'add order' tests

@pytest.mark.parametrize("order", bad_orders())
def test_except_add_order_01_bad_orders(order):
    print("Create order book")
    book = OrderBook()
    
    print("Adding incorrect order")
    with pytest.raises(BadOrderEx):
        assert type(book.add_order(order)) == int

def test_except_add_order_02_add_several_times():
    print("Create order book")
    book = OrderBook()

    print("Create simple order")
    order = Order(Side.BUY, 1, 1)

    print("Adding order first time")
    id = book.add_order(order)
    order.id = id
    
    print("Trying to add order two times")
    with pytest.raises(BadOrderEx):
        assert type(book.add_order(order)) == int

def test_except_add_order_03_add_del_add_chain():
    print("Create order book")
    book = OrderBook()
    order = random_order()
    id = book.add_order(order)
    order = book.del_order(id)
    
    print("Trying to add deleted order")
    with pytest.raises(BadOrderEx):
        assert type(book.add_order(order)) == int

# except 'del order' test

def test_except_del_order_01_order_id_not_exists():
    print("Create order book")
    book = OrderBook()
    id = 1234567890

    print("Trying to del not exist order")
    with pytest.raises(NoOrderEx):
        assert type(book.del_order(id)) == Order

# except 'get order' tests

def test_except_get_order_01_order_id_not_exists():
    print("Create order book")
    book = OrderBook()
    id = 1234567890

    print("Trying to get not exist order")
    with pytest.raises(NoOrderEx):
        assert type(book.get_order(id)) == Order

