import re
from typing import List
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            try:
                text += page.get_text()
            except AttributeError:
                text += page.getText()
    return text

def extract_education_section(text):
    """
    Fungsi untuk mengekstrak bagian Education dari teks resume
    
    Args:
        text (str): Teks lengkap dari resume
    
    Returns:
        str: Bagian education yang ditemukan, atau None jika tidak ada
    """
    
    # Pattern 1: Menangkap dari "Education" hingga section berikutnya atau akhir dokumen
    # Menggunakan case-insensitive matching
    pattern1 = r'(?i)^education\s*\n(.*?)(?=^\w+\s*\n|\Z)'
    
    # Pattern 2: Alternative pattern yang lebih fleksibel
    # Menangkap dari Education hingga baris yang dimulai dengan huruf kapital (section baru)
    pattern2 = r'(?i)education\s*\n((?:(?!^[A-Z][A-Za-z\s]+\n).*\n?)*)'
    
    # Pattern 3: Pattern yang menangkap Education dan semua baris setelahnya
    # hingga menemukan section baru atau kata kunci tertentu
    pattern3 = r'(?i)education\s*\n(.*?)(?=\n(?:experience|skills|certifications|interests|additional\s+information|professional\s+summary|summary|accomplishments|work history)\s*\n|\Z)'
    
    pattern4 = r'(?i)education and training\s*\n(.*?)(?=\n(?:experience|skills|certifications|interests|additional\s+information|professional\s+summary|summary|accomplishments|work history)\s*\n|\Z)'
    
    # Coba pattern pertama
    match = re.search(pattern1, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Coba pattern kedua jika yang pertama tidak berhasil
    match = re.search(pattern2, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Coba pattern ketiga sebagai fallback
    match = re.search(pattern3, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(pattern4, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_education_simple(text: str) -> str:
    """
    Fungsi sederhana untuk mengekstrak bagian Education
    """
    # Pattern sederhana yang menangkap dari Education hingga section berikutnya
    pattern = r'(?i)education\s*\n(.*?)(?=\n[A-Z][A-Za-z\s]*\n|\Z)'
    
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

# # Contoh penggunaan dengan sample text
# sample_text = """
# Experience
# Some experience details here
# Multiple lines of experience

# Education
# Northern Maine Community College 1994 Associate : Accounting City , State , USA
# Emphasis in Business
# 1994 Associates : Accounting City , State , USA GPA: GPA: 3.41
# Accounting GPA: 3.41 174 Hours, Quarter
# Attended Husson College, major Accounting 78 semester hours toward Bachelors degree.

# Skills
# Some skills here
# """

# # Test fungsi
# result = extract_education_section(sample_text)
# print("Hasil ekstraksi Education:")
# print("=" * 50)
# print(result)

# # Pattern regex yang bisa langsung digunakan
# print("\n" + "=" * 50)
# print("PATTERN REGEX YANG BISA DIGUNAKAN:")
# print("=" * 50)
# print("1. Pattern lengkap:")
# print(r'(?i)^education\s*\n(.*?)(?=^\w+\s*\n|\Z)')
# print("\n2. Pattern sederhana:")
# print(r'(?i)education\s*\n(.*?)(?=\n[A-Z][A-Za-z\s]*\n|\Z)')
# print("\n3. Pattern dengan section keywords:")
# print(r'(?i)education\s*\n(.*?)(?=\n(?:experience|skills|certifications|interests|additional\s+information)\s*\n|\Z)')

# print("\nPenjelasan Pattern:")
# print("- (?i) = case insensitive")
# print("- ^education\\s*\\n = mencari 'education' di awal baris diikuti whitespace dan newline")
# print("- (.*?) = capture group non-greedy untuk mengambil semua teks")
# print("- (?=...) = positive lookahead untuk menentukan akhir section")
# print("- \\Z = akhir string")
# print("- re.MULTILINE | re.DOTALL flags diperlukan")
if __name__ == "__main__":
    pdf_paths = [
        "../data/data/ACCOUNTANT/10554236.pdf",
        "../data/data/ACCOUNTANT/10674770.pdf",
        "../data/data/ACCOUNTANT/11163645.pdf"
    ]

    for path in pdf_paths:
        print(f"\n===== {path} =====")
        text = extract_text_from_pdf(path)
        edu = extract_education_section(text)
        if edu:
            print("Bagian Education ditemukan:")
            print("=" * 50)
            print(edu)
        else:
            print("Bagian Education tidak ditemukan.")
        