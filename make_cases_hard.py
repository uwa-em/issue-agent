from pathlib import Path

CASES = {
 "case6_two_files": ("Cart totals are off by a few cents for orders with several items. "
                     "Totals should be exact to 2 decimals.", {
  "pricing.py": "def line_total(price, qty):\n    return round(price * qty, 1)\n",
  "cart.py": "from pricing import line_total\n\ndef cart_total(items):\n    return round(sum(line_total(p, q) for p, q in items), 2)\n",
  "test_cart.py": '''from cart import cart_total

def test_single():
    assert cart_total([(9.99, 3)]) == 29.97

def test_mixed():
    assert cart_total([(0.1, 3), (19.99, 1)]) == 20.29

def test_simple():
    assert cart_total([(2.5, 2)]) == 5.0
'''}),
 "case7_vague": ("Users with a plus sign in their email, like bob+news@gmail.com, "
                 "can't sign up. The form says the email is invalid.", {
  "validators.py": '''import re

def is_valid_email(email):
    return re.match(r"^[A-Za-z0-9._]+@[A-Za-z0-9.-]+\\.[a-z]{2,}$", email) is not None
''',
  "test_validators.py": '''from validators import is_valid_email

def test_plus():
    assert is_valid_email("bob+news@gmail.com")

def test_dots():
    assert is_valid_email("a.b@x.org")

def test_invalid():
    assert not is_valid_email("bob@")
    assert not is_valid_email("@x.com")
    assert not is_valid_email("bob@x")
'''}),
 "case8_traceback": ("The weekly report crashes when the scores file ends with a blank line:\n"
                     "  File report.py, line 4, in top_scorer\n"
                     "    scores = load_scores(raw)\n"
                     "ValueError: not enough values to unpack (expected 2, got 1)\n"
                     "Fix it so trailing blank lines are fine.", {
  "data.py": "def load_scores(raw):\n    scores = {}\n    for line in raw.splitlines():\n        name, score = line.split(\",\")\n        scores[name] = int(score)\n    return scores\n",
  "report.py": "from data import load_scores\n\ndef top_scorer(raw):\n    scores = load_scores(raw)\n    return max(scores, key=scores.get)\n",
  "test_report.py": '''from report import top_scorer

def test_normal():
    assert top_scorer("ann,5\\nbob,9") == "bob"

def test_trailing_blank():
    assert top_scorer("ann,5\\nbob,9\\n\\n") == "bob"
'''}),
}

for name, (issue, files) in CASES.items():
    base = Path("cases") / name
    (base / "repo").mkdir(parents=True, exist_ok=True)
    (base / "issue.txt").write_text(issue)
    for fname, content in files.items():
        (base / "repo" / fname).write_text(content)
print("created", len(CASES), "hard cases")