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

def extract_skills_from_resume(text):
    """
    Fungsi untuk mengekstrak bagian Skills dari teks resume
    """
    
    # Pattern 1: Menangkap dari "skills" hingga section berikutnya atau akhir dokumen
    # Menggunakan case-insensitive matching
    pattern1 = r'(?i)^skills\s*\n(.*?)(?=^\w+\s*\n|\Z)'
    
    # Pattern 2: Alternative pattern yang lebih fleksibel
    # Menangkap dari skills hingga baris yang dimulai dengan huruf kapital (section baru)
    pattern2 = r'(?i)skills\s*\n((?:(?!^[A-Z][A-Za-z\s]+\n).*\n?)*)'
    
    
    # Pattern 3: Pattern yang menangkap skills dan semua baris setelahnya
    # hingga menemukan section baru atau kata kunci tertentu
    pattern3 = r'(?i)skills\s*\n(.*?)(?=\n(?:experience|skills|certifications|interests|additional\s+information|professional\s+summary|summary|accomplishments|work\s+history|highlights)\s*\n|\Z)'
    
    # Coba semua pattern
    patterns = [pattern1, pattern2, pattern3]
    
    # Coba pattern ketiga sebagai fallback
    match = re.search(pattern3, text, re.MULTILINE | re.DOTALL)
    if match:
        result = match.group(1).strip()
        print(match.group(1).strip())
        if not re.search(r'(?i)(?:work\s+history|employment|experience|education)', result):
            return result
    
    # Coba pattern pertama
    match = re.search(pattern1, text, re.MULTILINE | re.DOTALL)
    if match:
        result = match.group(1).strip()
        print(match.group(1).strip())
        if not re.search(r'(?i)(?:work\s+history|employment|experience|education)', result):
            return result
    
    # Coba pattern kedua jika yang pertama tidak berhasil
    match = re.search(pattern2, text, re.MULTILINE | re.DOTALL)
    if match:
        result = match.group(1).strip()
        print(match.group(1).strip())
        if not re.search(r'(?i)(?:work\s+history|employment|experience|education)', result):
            return result
    
    
    return None

def extract_skills_simple(text):
    """
    Fungsi sederhana untuk mengekstrak skills
    """
    # Pattern yang lebih komprehensif
    pattern = r'(?i)Skills\s*[:\-]?\s*\n?(.*?)(?=\n(?:[A-Z][a-zA-Z\s]*(?:\n|:)|Additional Information|$))'
    
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

# # Contoh penggunaan
# sample_texts = [
#     """
# Experience
# Some work experience here

# Skills
# Python, Java, JavaScript, SQL, HTML, CSS, React, Node.js, Git, Docker
# Machine Learning, Data Analysis, Problem Solving

# skills
# Bachelor's Degree
#     """,
    
#     """
# Previous Job Experience

# Skills:
# - Programming: Python, Java, C++
# - Databases: MySQL, PostgreSQL, MongoDB  
# - Web Development: HTML, CSS, JavaScript, React
# - Tools: Git, Docker, AWS

# Additional Information
# Other details here
#     """,
    
#     """
# Work History

# Skills
# accounting, accounts payable, Accounts Receivable, ADP, advertising, AR, balance sheet, balance, bank reconciliations, benefits, billing, billings, book keeping, budget, cash flow projections, cash flow, controller, Credit, clients, data collection, delivery, documentation, email, Finance, financial, financial reporting, financial statements, fixed assets, General Ledger, inventory, job costing, ledger, legal, materials, meetings, Microsoft Access, Microsoft Excel, Excel, Microsoft Word, negotiating, DBA, Payables, payroll, Peachtree, processes, coding, purchasing, Express, Quick Books, QuickBooks, Research, Sage, Sales, Spreadsheet, Tax, software support, valuation, year-end

# Additional Information
#     """
# ]

# # Test pada contoh teks
# print("=== Testing Regex Patterns ===\n")

# for i, sample in enumerate(sample_texts, 1):
#     print(f"Sample Text {i}:")
#     print("-" * 50)
    
#     # Test dengan fungsi komprehensif
#     results = extract_skills_from_resume(sample)
#     if results:
#         for result in results:
#             print(f"{result['pattern_used']}: {result['skills_text'][:100]}...")
    
#     # Test dengan fungsi sederhana
#     simple_result = extract_skills_simple(sample)
#     if simple_result:
#         print(f"Simple Pattern: {simple_result[:100]}...")
    
#     print("\n" + "="*70 + "\n")

# # Regex pattern yang direkomendasikan
# print("RECOMMENDED REGEX PATTERNS:")
# print("="*50)
# print("1. Basic Pattern:")
# print(r"(?i)Skills\s*[:\-]?\s*(.*?)(?=\n\n|\n[A-Z][a-zA-Z\s]*\n|$)")
# print()
# print("2. Multi-line Pattern:")
# print(r"(?i)Skills\s*\n?(.*?)(?=\n(?:[A-Z][a-zA-Z\s]*(?:\n|:)|Additional Information|$))")
# print()
# print("3. Flexible Pattern:")
# print(r"(?i)(?:^|\n)Skills\s*[:\-]?\s*\n?(.*?)(?=\n(?:[A-Z][a-zA-Z\s]*(?:\n|:)|$))")
if __name__ == "__main__":
    pdf_paths = [
        "../data/data/ACCOUNTANT/10554236.pdf",
        "../data/data/ACCOUNTANT/10674770.pdf",
        "../data/data/ACCOUNTANT/11163645.pdf"
    ]

    for path in pdf_paths:
        print(f"\n===== {path} =====")
        text = extract_text_from_pdf(path)
        edu = extract_skills_from_resume(text)
        if edu:
            print("Bagian skills ditemukan:")
            print("=" * 50)
            print(edu)
        else:
            print("Bagian skills tidak ditemukan.")