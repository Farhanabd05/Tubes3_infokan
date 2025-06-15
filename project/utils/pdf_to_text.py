
import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Ekstrak teks dari file PDF menjadi satu string.
    """
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            # print(dir(page))
            try:
                # Try the newer method first
                text += page.get_text()
            except AttributeError:
                # Fall back to older method name
                text += page.getText()
    return text

def load_all_cv_texts(cv_root_folder: str) -> list[dict]:
    """
    Memuat semua file PDF dari folder data/ dan mengubahnya menjadi teks.
    Mengembalikan list of dicts dengan key: 'path', 'role', 'text'.
    """
    all_cv_data = []

    for role in os.listdir(cv_root_folder):
        role_folder = os.path.join(cv_root_folder, role)
        if not os.path.isdir(role_folder):
            continue

        for filename in os.listdir(role_folder):
            if filename.lower().endswith(".pdf"):
                full_path = os.path.join(role_folder, filename)
                extracted = extract_text_from_pdf(full_path)
                all_cv_data.append({
                    "path": full_path,
                    "filename": filename,
                    "text": extracted
                })

    return all_cv_data

def test_pdf_extraction():
    cv_data = load_all_cv_texts("../data")  # atau sesuaikan
    for data in cv_data[:3]:  # tampilkan 3 contoh
        print("="*40)
        print(f"File: {data['filename']} ({data['role']})")
        print(data['text'][:500], "...")  # tampilkan 500 karakter pertama

if __name__ == "__main__":
    test_pdf_extraction()
