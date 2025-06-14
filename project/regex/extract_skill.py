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
    
    # Pattern 1: Skills sebagai header dengan konten di bawahnya
    # Menangkap dari "Skills" hingga section berikutnya atau akhir dokumen
    pattern1 = r'(?i)^Skills\s*\n(.*?)(?=\n[A-Z][a-zA-Z\s]*\n|\n[A-Z][a-zA-Z\s]*:|$)'
    
    # Pattern 2: Skills dengan konten dalam satu paragraf
    pattern2 = r'(?i)Skills\s*[:\-]?\s*(.*?)(?=\n\n|\n[A-Z][a-zA-Z\s]*\n|$)'
    
    # Pattern 3: Skills di akhir dokumen
    pattern3 = r'(?i)Skills\s*[:\-]?\s*(.*?)$'
    
    # Pattern 4: Skills dengan bullet points atau list
    pattern4 = r'(?i)Skills\s*\n((?:.*\n)*?)(?=\n[A-Z][a-zA-Z\s]*\n|\n[A-Z][a-zA-Z\s]*:|$)'
    
    # Coba semua pattern
    patterns = [pattern1, pattern2, pattern3, pattern4]
    
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
    
    # Coba pattern ketiga sebagai fallback
    match = re.search(pattern4, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
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

# Education
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
            print("Bagian Education ditemukan:")
            print("=" * 50)
            print(edu)
        else:
            print("Bagian Education tidak ditemukan.")