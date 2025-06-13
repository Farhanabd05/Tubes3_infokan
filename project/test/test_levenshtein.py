import sys
import os
# Add the parent directory (project/) to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.levenshtein import levenshtein_distance

def test_levenshtein():
    test_cases = [
        ("kitten", "sitting", 3),
        ("flaw", "lawn", 2),
        ("gumbo", "gambol", 2),
        ("book", "back", 2),
        ("data", "data", 0),
    ]

    for a, b, expected in test_cases:
        result = levenshtein_distance(a, b)
        print(f"Distance('{a}', '{b}') = {result} | Expected: {expected}")
        assert result == expected, f"Mismatch on '{a}' <-> '{b}'"

# Jalankan test
test_levenshtein()
