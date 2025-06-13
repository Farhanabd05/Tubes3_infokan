# file: src/kmp_utils.py

def compute_lps(pattern: str) -> list[int]:
    """
    Bangun array LPS (longest proper prefix which is also suffix)
    untuk pola 'pattern'.
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # panjang prefix-suffix saat ini
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # mundur ke nilai LPS sebelumnya
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text: str, pattern: str) -> list[int]:
    """
    Cari semua kemunculan 'pattern' di 'text' menggunakan KMP.
    Kembalikan list posisi (0-based) di mana pattern mulai cocok.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return []

    lps = compute_lps(pattern)
    results = []
    i = j = 0  # i untuk text, j untuk pattern

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                # ketemu match berakhir di i-1, maka start = i-m
                results.append(i - m)
                j = lps[j - 1]
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return results