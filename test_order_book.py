import pytest
from order_book import Order
from order_book import OrderBook

def test_succes_order_book_01_create():
    book = OrderBook()

    assert type(book.orders) == dict
    assert len(book.orders) == 0

def data_good_orders() -> list:
    yield Order("buy", 1, 2)
    yield Order("sell", 3, 4)
    yield Order("buy", 5.6, 7.8)
    yield Order("sell", 0.0000000000000001, 1000000000000000.0)

@pytest.mark.parametrize("order", data_good_orders())
def test_succes_add_order_01_one_order(order):
    book = OrderBook()
    order = Order("sell", 6, 1)
    id = book.add_order(order)

    assert id == order.id
    assert order.state == "opened"
    assert len(book.orders) == 1
    assert list(book.orders.values()) == [order]
    assert list(book.orders.keys()) == [order.id]

def test_success_add_order_02_several_orders():
    book = OrderBook()
    order1 = Order("buy", 3, 4)
    order2 = Order("sell", 7, 5)
    book.add_order(order1)
    book.add_order(order2)

    assert len(book.orders) == 2
    assert list(book.orders.values()) == [order1, order2]
    assert list(book.orders.keys()) == [order1.id, order2.id]

@pytest.mark.parametrize("order", data_good_orders())
def test_success_del_order_01_one_order(order):
    book = OrderBook()
    order = Order("buy", 2, 6)
    book.add_order(order)
    order2 = book.del_order(order.id)

    assert order2 == order
    assert len(book.orders) == 0
    assert order.state == "canceled"

@pytest.mark.parametrize("order", data_good_orders())
def test_succes_get_order_01_one_order(order):
    book = OrderBook()
    order = Order("sell", 8, 7)
    book.add_order(order)
    order2 = book.get_order(order.id)

    assert order.state == "opened"
    assert order2 == order
    assert len(book.orders) == 1
    assert book.orders == { order2.id: order2 }

def test_market_data_01_check_struct():
    book = OrderBook()
    order1 = Order("buy", 1, 8)
    order2 = Order("sell", 9, 9)
    book.add_order(order1)
    book.add_order(order2)
    market = book.market_data()

    assert market == { 
        "asks": [{ "price": order2.price, "quantity": order2.quantity }], 
        "bids": [{ "price": order1.price, "quantity": order1.quantity }] 
    }

def test_market_data_02_check_sorting():
    book = OrderBook()
    order1 = Order("buy", 1, 1)
    order2 = Order("sell", 9, 2)
    order3 = Order("buy", 3, 3)
    order4 = Order("sell", 7, 4)
    order5 = Order("buy", 2, 5)
    order6 = Order("sell", 8, 6)
    
    book.add_order(order1)
    book.add_order(order2)
    book.add_order(order3)
    book.add_order(order4)
    book.add_order(order5)
    book.add_order(order6)
    
    market = book.market_data()

    assert market["asks"] == sorted(market["asks"], key = lambda d: d["price"], reverse = True)
    assert market["bids"] == sorted(market["bids"], key = lambda d: d["price"], reverse = True)

def test_market_data_03_check_agregation():
    book = OrderBook()
    order1 = Order("buy", 1, 1)
    order2 = Order("sell", 2, 1)
    order3 = Order("buy", 1, 1)
    order4 = Order("sell", 2, 1)
    
    book.add_order(order1)
    book.add_order(order2)
    book.add_order(order3)
    book.add_order(order4)

    market = book.market_data()

    assert market == { 
        "asks": [{ "price": 2.0, "quantity": 2.0 }], 
        "bids": [{ "price": 1.0, "quantity": 2.0 }] 
    }

def data_bad_orders():
    yield Order("foo", 1, 2)
    yield Order("buy", 0, 3)
    yield Order("sell", 4, -1)
    yield Order([], 5, 6)
    yield Order("buy", "$7", 8)
    yield Order("sell", 9, "1PC")
    yield Order("buy", 0.001, -0.01)
    yield Order("sell", -0.001, 0.01)

@pytest.mark.parametrize("order", data_bad_orders())
def test_except_add_order_01_bad_orders(order):
    book = OrderBook()
    with pytest.raises(Exception):
        book.add_order(order)
