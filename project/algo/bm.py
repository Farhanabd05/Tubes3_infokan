# Boyer Moore String Search Algorithm
def build_last_occurrence(pattern:str, charset=None) -> dict:
    """
    Builds last occurrence table for 'pattern'.
    returns a map of char and their last index position.
    """
    if charset is None:
        charset = set(pattern) 

    last_occurrence = {char: -1 for char in charset}
    for i, char in enumerate(pattern):
        last_occurrence[char] = i
    return last_occurrence

def boyer_moore_search(text: str, pattern: str) -> list[int]:
    """
    Finds all occurences of pattern in text.
    Returns a list of start indexes.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return []

    last_occurrence = build_last_occurrence(pattern)
    results = []
    s = 0  # shift

    while s <= n - m:
        j = m - 1 # index of last char in pattern
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            results.append(s) 
            s += (s + m < n) and (m - last_occurrence.get(text[s + m], -1)) or 1
        else:
            s += max(1, j - last_occurrence.get(text[s + j], -1))
    
    return results