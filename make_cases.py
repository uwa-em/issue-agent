from pathlib import Path

CASES = {
 "case1_email": ("Login fails for users who type their email with capital letters. "
                 "normalize_email should return a lowercase, trimmed email.", {
  "users.py": "def normalize_email(email):\n    return email.strip()\n",
  "test_users.py": '''from users import normalize_email

def test_lowercases():
    assert normalize_email("  Bob@Example.COM ") == "bob@example.com"

def test_strips():
    assert normalize_email(" a@b.com ") == "a@b.com"
'''}),
 "case2_pagination": ("Page 1 of the results skips the first items. Pages are 1-indexed: "
                      "page 1 should return the first `size` items.", {
  "paging.py": "def paginate(items, page, size):\n    start = page * size\n    return items[start:start + size]\n",
  "test_paging.py": '''from paging import paginate

def test_first_page():
    assert paginate(list(range(10)), 1, 3) == [0, 1, 2]

def test_second_page():
    assert paginate(list(range(10)), 2, 3) == [3, 4, 5]

def test_partial_last_page():
    assert paginate(list(range(10)), 4, 3) == [9]
'''}),
 "case3_average": ("The dashboard crashes with ZeroDivisionError when a user has no scores. "
                   "average of an empty list should return 0.", {
  "stats.py": "def average(nums):\n    return sum(nums) / len(nums)\n",
  "test_stats.py": '''from stats import average

def test_average():
    assert average([2, 4, 6]) == 4

def test_empty():
    assert average([]) == 0
'''}),
 "case4_palindrome": ("is_palindrome returns False for 'Racecar' and for phrases with spaces or "
                      "punctuation. It should ignore case, spaces and punctuation.", {
  "text.py": "def is_palindrome(s):\n    return s == s[::-1]\n",
  "test_text.py": '''from text import is_palindrome

def test_case():
    assert is_palindrome("Racecar")

def test_phrase():
    assert is_palindrome("A man, a plan, a canal: Panama")

def test_negative():
    assert not is_palindrome("hello")
'''}),
 "case5_wordcount": ("word_count is wrong when the text has extra spaces or is empty. "
                     "It should count words, not spaces.", {
  "text_utils.py": "def word_count(text):\n    return len(text.split(\" \"))\n",
  "test_text_utils.py": '''from text_utils import word_count

def test_simple():
    assert word_count("hello world") == 2

def test_extra_spaces():
    assert word_count("hello   world") == 2

def test_empty():
    assert word_count("") == 0

def test_padded():
    assert word_count("  hi  ") == 1
'''}),
}

for name, (issue, files) in CASES.items():
    base = Path("cases") / name
    (base / "repo").mkdir(parents=True, exist_ok=True)
    (base / "issue.txt").write_text(issue)
    for fname, content in files.items():
        (base / "repo" / fname).write_text(content)
print("created", len(CASES), "cases")