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
    n = len(text) 
    m= len(pattern) 
    lps = compute_lps(pattern) 
    results = []
    i=j=0
    while i<n:
        if pattern[j]== text[i]:
            i+= 1
            j+=1
        if j == m:
            print("Pattern found at index:", i-j)
            results.append(i-j)
            j= lps [j-1]
        else:
            if i < n and pattern[j]!= text[i]:
                if j!= 0:
                    j= lps [j-1]
                else:
                    i+=1
            else:
                i+=1
    return results