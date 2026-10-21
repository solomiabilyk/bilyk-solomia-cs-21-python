import pytest
from order_manager import Order  # Припускається, що клас Order знаходиться в файлі order_manager.py[cite: 4]


# --- Тести для методу total() ---

def test_total_valid_items():
    """Перевірка розрахунку загальної суми для коректного списку товарів."""
    items = [
        {'price': 100, 'quantity': 2},  # 200
        {'price': 50, 'quantity': 1},   # 50
        {'price': 25.5, 'quantity': 4}  # 102
    ]
    order = Order(id=1, items=items)
    assert order.total() == 352.0


def test_total_empty_items():
    """Перевірка розрахунку суми для пустого замовлення."""
    order = Order(id=2, items=[])
    assert order.total() == 0


def test_total_zero_quantity_or_price():
    """Перевірка межових значень: нульова ціна та нульова кількість."""
    items = [
        {'price': 0, 'quantity': 10},
        {'price': 100, 'quantity': 0}
    ]
    order = Order(id=3, items=items)
    assert order.total() == 0


# --- Тесты для методу most_expensive() ---

def test_most_expensive_valid_items():
    """Перевірка пошуку найдорожчого товару."""
    item1 = {'name': 'Item 1', 'price': 10, 'quantity': 5}
    item2 = {'name': 'Item 2', 'price': 100, 'quantity': 1}
    item3 = {'name': 'Item 3', 'price': 50, 'quantity': 2}
    
    order = Order(id=1, items=[item1, item2, item3])
    assert order.most_expensive() == item2


def test_most_expensive_empty_items_raises_value_error():
    """Перевірка виклику ValueError при пошуку найдорожчого товару в пустому замовленні."""
    order = Order(id=2, items=[])
    with pytest.raises(ValueError):
        order.most_expensive()


# --- Тести для методу apply_discount() ---

@pytest.mark.parametrize("valid_percent", [0, 50, 100, 25.5])
def test_apply_discount_valid_percent(valid_percent):
    """Перевірка застосування коректних відсотків знижки (включаючи межові 0% і 100%)."""
    items = [{'price': 100, 'quantity': 1}, {'price': 200, 'quantity': 2}]
    order = Order(id=1, items=items)
    
    order.apply_discount(valid_percent)
    
    expected_price_1 = 100 - (100 * valid_percent / 100)
    expected_price_2 = 200 - (200 * valid_percent / 100)
    
    assert pytest.approx(order.items[0]['price']) == expected_price_1
    assert pytest.approx(order.items[1]['price']) == expected_price_2


@pytest.mark.parametrize("invalid_percent", [-1, -0.1, 100.1, 150])
def test_apply_discount_invalid_percent_raises_value_error(invalid_percent):
    """Перевірка виклику ValueError при невалідному відсотку знижки (менше 0 або більше 100)."""
    items = [{'price': 100, 'quantity': 1}]
    order = Order(id=1, items=items)
    
    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(invalid_percent)


def test_apply_discount_updates_all_items_and_total():
    """Перевірка, що знижка дійсно змінює ціни всіх елементів та загальну суму."""
    items = [{'price': 100, 'quantity': 2}, {'price': 50, 'quantity': 1}]
    order = Order(id=1, items=items)
    
    order.apply_discount(20)  # 20% знижки
    
    assert order.items[0]['price'] == 80.0
    assert order.items[1]['price'] == 40.0
    assert order.total() == (80.0 * 2) + (40.0 * 1)


def test_apply_discount_empty_items():
    """Перевірка застосування знижки до пустого списку товарів (не повинно викликати помилок)."""
    order = Order(id=1, items=[])
    order.apply_discount(10)
    assert order.items == []


# --- Тести для методу __repr__() ---

def test_repr_formatting():
    """Перевірка рядкового представлення об'єкта Order."""
    items = [{'price': 10, 'quantity': 1}, {'price': 20, 'quantity': 2}]
    order = Order(id=42, items=items)
    assert repr(order) == "<Order 42: 2 items>"


def test_repr_empty_items():
    """Перевірка рядкового представлення об'єкта Order з пустим списком товарів."""
    order = Order(id=99, items=[])
    assert repr(order) == "<Order 99: 0 items>"