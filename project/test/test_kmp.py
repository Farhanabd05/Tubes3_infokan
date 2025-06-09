# file: src/test_kmp_utils.py
import sys
import os
# Add the parent directory (project/) to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.kmp import compute_lps, kmp_search

def test_compute_lps_basic():
    # pola 'AAAB'
    lps = compute_lps("AAAB")
    # paling sederhana, lps harus [0,1,2,0]
    assert lps == [0,1,2,0], f"LPS salah: {lps}"

def test_kmp_search_found():
    text = "ababcabcab"
    pattern = "abc"
    positions = kmp_search(text, pattern)
    assert positions == [2,5], f"Expected [2,5], got {positions}"

def test_kmp_search_no_match():
    assert kmp_search("aaaaa", "b") == [], "Seharusnya tidak ada match"

def test_kmp_search_empty_pattern():
    # pola kosong dianggap tidak valid, kembalikan []
    assert kmp_search("anything", "") == [], "Pattern kosong harus []"

def test_kmp_search_overlap():
    # pola 'ABA' di 'ABABA' muncul di 0 dan 2
    assert kmp_search("ABABA", "ABA") == [0,2], "Overlap matches gagal"

if __name__ == "__main__":
    test_compute_lps_basic()
    test_kmp_search_found()
    test_kmp_search_no_match()
    test_kmp_search_empty_pattern()
    test_kmp_search_overlap()
    print("✓ Semua test KMP lulus.")
