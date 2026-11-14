from text import is_palindrome

def test_case():
    assert is_palindrome("Racecar")

def test_phrase():
    assert is_palindrome("A man, a plan, a canal: Panama")

def test_negative():
    assert not is_palindrome("hello")
