import math
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


def dynamicLevenshteinSearch(text: str, pattern: str, tolerance_percent: float = 0.125, max_edits: int = 4) -> tuple[int, list[str]]:
    # Hitung ambang batas (allowed_edits) secara dinamis
    patternLen = len(pattern)
    if patternLen == 0:
        return 0, []
    allowedEdits = min(math.ceil(tolerance_percent * patternLen), max_edits)
    words = text.split()
    count = 0
    matched_words = []
    pattern_lower = pattern.lower()
    for word in words:
        # allowedEdits sebagai threshold dinamis
        if levenshtein_distance(word.lower(), pattern_lower) <= allowedEdits: 
            count += 1
            matched_words.append(word)
    return count, matched_words

def tune_threshold():
    """
    Simple threshold tuning function
    """
    # Test keywords untuk tuning
    test_keywords = ["python", "javascript", "react", "html", "css", "java", "sql"]
    
    # Test dengan typos yang umum terjadi
    test_cases = [
        ("python", ["pyton", "phyton", "pythn"]),  # Missing/extra letters
        ("javascript", ["javscript", "javasript", "javascrip"]),  # Common typos
        ("react", ["reac", "reactt", "reat"]),  # Missing/extra letters
        ("html", ["htm", "htlm", "htmll"]),  # Common typos
    ]
    
    threshold_candidates = [0.125, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    
    print("🔧 THRESHOLD TUNING RESULTS:")
    print("=" * 60)
    
    best_threshold = 0.25
    best_score = 0
    
    for threshold in threshold_candidates:
        correct_matches = 0
        total_tests = 0
        
        for correct_word, typos in test_cases:
            for typo in typos:
                total_tests += 1
                # Simulasi text yang mengandung typo
                test_text = f"experienced in {typo} programming"
                count, matches = dynamicLevenshteinSearch(test_text, correct_word, threshold)
                if count > 0:  # Jika berhasil match
                    correct_matches += 1
        
        accuracy = (correct_matches / total_tests) * 100
        print(f"Threshold {threshold:.2f}: {correct_matches}/{total_tests} matches ({accuracy:.1f}% accuracy)")
        
        if accuracy > best_score:
            best_score = accuracy
            best_threshold = threshold
    
    print("=" * 60)
    print(f"🎯 OPTIMAL THRESHOLD: {best_threshold} (Accuracy: {best_score:.1f}%)")
    print("=" * 60)
    
    return best_threshold

if __name__ == "__main__":
    # Jalankan tuning threshold
    optimal_threshold = tune_threshold()
    print(f"Optimal threshold untuk dynamicLevenshteinSearch: {optimal_threshold}")
# Dummy data sesuai SQL schema
