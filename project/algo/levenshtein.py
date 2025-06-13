def levenshtein_distance(a: str, b: str) -> int:
    """
    Menghitung jarak Levenshtein antara dua string.
    """
    len_a, len_b = len(a), len(b)

    # Buat matriks ukuran (len_a+1) x (len_b+1)
    dp = [[0 for _ in range(len_b + 1)] for _ in range(len_a + 1)]

    # Inisialisasi baris dan kolom pertama
    for i in range(len_a + 1):
        dp[i][0] = i  # Biaya menghapus semua karakter dari a
    for j in range(len_b + 1):
        dp[0][j] = j  # Biaya menambahkan semua karakter ke a

    # Isi matriks
    for i in range(1, len_a + 1):
        for j in range(1, len_b + 1):
            if a[i - 1] == b[j - 1]:
                cost = 0  # karakter sama, tidak ada biaya
            else:
                cost = 1  # karakter beda, ada biaya subtitusi

            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Hapus
                dp[i][j - 1] + 1,      # Tambah
                dp[i - 1][j - 1] + cost  # Substitusi
            )

    return dp[len_a][len_b]
