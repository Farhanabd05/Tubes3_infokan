import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.ahocor import AhoCorasick


def test_aho_search_found():
    text = "my name is abc and adc is not my name"
    words = ["abc", "name"]
    positions = set(AhoCorasick.search(text, words))
    expected = {(11, "abc"), (3, "name"), (33, "name")}
    assert positions == expected, f"Expected {expected}, got {positions}"
def test_aho_search_no_match():
    positions = AhoCorasick.search("my name is abc and adc is not my name", ["xyz", "az"])
    assert positions == [], "Seharusnya tidak ada match"

def test_aho_search_empty_pattern():
    # pola kosong dianggap tidak valid, kembalikan []
    assert AhoCorasick.search("anything", "") == [], "Pattern kosong harus []"

if __name__ == "__main__":
    test_aho_search_found()
    test_aho_search_no_match()
    test_aho_search_empty_pattern()
    print("✓ Semua test aho lulus.")
