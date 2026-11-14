from users import normalize_email

def test_lowercases():
    assert normalize_email("  Bob@Example.COM ") == "bob@example.com"

def test_strips():
    assert normalize_email(" a@b.com ") == "a@b.com"
