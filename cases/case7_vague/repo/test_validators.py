from validators import is_valid_email

def test_plus():
    assert is_valid_email("bob+news@gmail.com")

def test_dots():
    assert is_valid_email("a.b@x.org")

def test_invalid():
    assert not is_valid_email("bob@")
    assert not is_valid_email("@x.com")
    assert not is_valid_email("bob@x")
