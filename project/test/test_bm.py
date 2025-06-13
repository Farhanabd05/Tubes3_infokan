import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.bm import build_last_occurrence, boyer_moore_search

def test_build_last_occurrence(string="CBAABCAAAB"):
    # pola 'AAAB'
    lps = build_last_occurrence("AAAB", charset=set(string))
    assert lps == {"A":2,"B":3,"C":-1}, f"LPS salah: {lps}"

def test_bm_search_found():
    text = "ababcabcab"
    pattern = "abc"
    positions = boyer_moore_search(text, pattern)
    assert positions == [2,5], f"Expected [2,5], got {positions}"

def test_bm_search_no_match():
    assert boyer_moore_search("aaaaa", "b") == [], "Seharusnya tidak ada match"

def test_bm_search_empty_pattern():
    # pola kosong dianggap tidak valid, kembalikan []
    assert boyer_moore_search("anything", "") == [], "Pattern kosong harus []"

def test_bm_search_overlap():
    # pola 'ABA' di 'ABABA' muncul di 0 dan 2
    assert boyer_moore_search("ABABA", "ABA") == [0,2], "Overlap matches gagal"

if __name__ == "__main__":
    test_build_last_occurrence()
    test_bm_search_found()
    test_bm_search_no_match()
    test_bm_search_empty_pattern()
    test_bm_search_overlap()
    print("✓ Semua test bm lulus.")
