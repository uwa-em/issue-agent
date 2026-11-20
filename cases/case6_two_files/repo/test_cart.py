from cart import cart_total

def test_single():
    assert cart_total([(9.99, 3)]) == 29.97

def test_mixed():
    assert cart_total([(0.1, 3), (19.99, 1)]) == 20.29

def test_simple():
    assert cart_total([(2.5, 2)]) == 5.0
