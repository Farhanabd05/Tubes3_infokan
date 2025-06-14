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

def extract_experience_section(text: str) -> List[str]:
    """
    Ekstrak entri pengalaman kerja berdasarkan pola tanggal kerja,
    menangani job title dan company info yang bisa di baris terpisah atau sama.
    """
    lines = text.split('\n')
    results = []

    # Update regex untuk menangani line breaks dan variasi format
    date_pattern = re.compile(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*\n?\s*to\s*\n?\s*(January|February|March|April|May|June|July|August|September|October|November|December|Present)\s+\d{4}",
        re.IGNORECASE | re.MULTILINE
    )
    
    # Tambahkan pattern untuk format MM/YYYY to MM/YYYY
    numeric_date_pattern = re.compile(
        r"\b(0[1-9]|1[0-2])/\d{4}\s*to\s*(0[1-9]|1[0-2])/\d{4}\b",
        re.IGNORECASE
    )

    # Tambahkan pattern untuk format singkat bulan (Aug 2005 to Aug 2007, Aug 2007 to Current)
    short_month_pattern = re.compile(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*to\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Current)\s*(?:\d{4})?\b",
        re.IGNORECASE
    )

    
    # Gabungkan teks untuk menangani pattern yang tersebar di multiple lines
    full_text = '\n'.join(lines)
    
    # Cari semua matches dari semua pattern
    matches = (list(date_pattern.finditer(full_text)) + 
               list(numeric_date_pattern.finditer(full_text)) + 
               list(short_month_pattern.finditer(full_text)))
    
    # Sort matches berdasarkan posisi dalam teks
    matches.sort(key=lambda x: x.start())
    
    for match in matches:
        match_start = match.start()
        match_end = match.end()
        lines_before_match = full_text[:match_start].count('\n')
        lines_after_match = full_text[:match_end].count('\n')
        
        # Ambil tanggal yang sudah ditemukan
        date_info = match.group().replace('\n', ' ').strip()
        
        title_line = ""
        company_line = ""
        
        # Cek apakah tanggal berada di tengah baris (ada teks sebelum dan sesudah)
        current_line_start = full_text.rfind('\n', 0, match_start) + 1
        current_line_end = full_text.find('\n', match_end)
        if current_line_end == -1:
            current_line_end = len(full_text)
        
        current_line = full_text[current_line_start:current_line_end].strip()
        
        # Ekstrak bagian sebelum dan sesudah tanggal dalam baris yang sama
        text_before_date = current_line[:match_start - current_line_start].strip()
        text_after_date = current_line[match_end - current_line_start:].strip()
        
        # Prioritas 1: Cek apakah ada teks di baris yang sama dengan tanggal
        if text_before_date and len(text_before_date.split()) < 6:
            title_line = text_before_date
        elif text_after_date and len(text_after_date.split()) < 6:
            title_line = text_after_date
        
        # Prioritas 2: Jika tidak ada di baris yang sama, cek baris sebelumnya
        if not title_line and lines_before_match > 0 and lines_before_match < len(lines):
            prev_line = lines[lines_before_match - 1].strip()
            if len(prev_line.split()) < 6 and prev_line:
                title_line = prev_line
        
        # Prioritas 3: Ambil company info dari baris setelahnya jika tidak ada di baris yang sama
        if not text_after_date and lines_after_match < len(lines):
            next_line = lines[lines_after_match].strip()
            if len(next_line.split()) < 6 and next_line:
                company_line = next_line
        elif text_after_date and not title_line:
            # Jika text_after_date tidak dijadikan title, maka bisa jadi company
            if len(text_after_date.split()) < 6:
                company_line = text_after_date
        
        # Jika ada text_before_date dan text_after_date, gunakan keduanya
        if text_before_date and text_after_date:
            if len(text_before_date.split()) < 6 and len(text_after_date.split()) < 6:
                title_line = text_before_date
                company_line = text_after_date
        
        # Gabungkan semua komponen
        combined = "\n".join(filter(None, [title_line, date_info, company_line]))
        results.append(combined)

    return results

if __name__ == "__main__":
    pdf_paths = [
        "../data/data/ACCOUNTANT/10554236.pdf",
        "../data/data/ACCOUNTANT/10674770.pdf",
        "../data/data/ACCOUNTANT/11163645.pdf"
    ]

    for path in pdf_paths:
        print(f"\n===== {path} =====")
        text = extract_text_from_pdf(path)
        experiences = extract_experience_section(text)
        for exp in experiences:
            print(exp)
            print("---")