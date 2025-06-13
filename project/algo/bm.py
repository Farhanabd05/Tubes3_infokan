# Boyer Moore String Search Algorithm
def build_last_occurrence(pattern:str, charset=None) -> dict:
    """
    Bangun tabel last occurrence untuk pola 'pattern'.
    Tabel ini menyimpan indeks terakhir kemunculan setiap karakter.
    """
    if charset is None:
        charset = set(pattern)  # gunakan karakter unik dari pola

    last_occurrence = {char: -1 for char in charset}
    for i, char in enumerate(pattern):
        last_occurrence[char] = i
    return last_occurrence

def boyer_moore_search(text: str, pattern: str) -> list[int]:
    """
    Cari semua kemunculan 'pattern' di 'text' menggunakan Boyer-Moore.
    Kembalikan list posisi (0-based) di mana pattern mulai cocok.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return []

    last_occurrence = build_last_occurrence(pattern)
    results = []
    s = 0  # shift

    while s <= n - m:
        j = m - 1  # indeks terakhir dari pola
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            results.append(s)  # ditemukan match
            s += (s + m < n) and (m - last_occurrence.get(text[s + m], -1)) or 1
        else:
            s += max(1, j - last_occurrence.get(text[s + j], -1))
    
    return results