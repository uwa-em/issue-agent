from report import top_scorer

def test_normal():
    assert top_scorer("ann,5\nbob,9") == "bob"

def test_trailing_blank():
    assert top_scorer("ann,5\nbob,9\n\n") == "bob"
