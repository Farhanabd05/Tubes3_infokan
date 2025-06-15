Berikut adalah draft file `README.md` yang sesuai dengan spesifikasi dari dokumen `Spesifikasi Tugas Besar 3 Stima 2024_2025.pdf`:

---

# CV Analyzer ATS - Tubes 3 Stima 2024/2025

## 🧠 Penjelasan Algoritma

### 🔍 Knuth-Morris-Pratt (KMP)

Algoritma KMP digunakan untuk pencocokan string secara efisien dengan pendekatan prefix-suffix table (`LPS`). KMP menghindari pemeriksaan ulang karakter yang sudah cocok sebelumnya sehingga dapat mencari pattern dalam waktu linear terhadap panjang teks dan pattern (O(N + M)).

### 🧠 Boyer-Moore (BM)

Boyer-Moore adalah algoritma pencocokan string yang menggunakan strategi “lompat” berdasarkan karakter terakhir dalam pattern. Dengan memanfaatkan tabel *Last Occurrence*, BM sering kali lebih cepat dalam praktik, terutama untuk pattern yang panjang.

## ⚙️ Requirements & Instalasi

### Python Version

* Python 3.9+

### Instalasi dengan [uv](https://github.com/astral-sh/uv)

Jika kamu menggunakan **uv** sebagai dependency manager:

```bash
uv venv
```bash
uv add flet mysql-connector-python PyMuPDF faker
```

Atau install dari `pyproject.toml`:

```bash
uv sync
```

### Dependencies

```toml
[project]
name = "cv-analyzer-ats"
version = "0.1.0"
description = "CV Analyzer ATS using KMP and Boyer-Moore algorithms"
authors = [
    {name = "Abdullah Farhan", email = "13523042@std.stei.itb.ac.id"},
    {name = "William Andrian", email = "13523006@std.stei.itb.ac.id"},
    {name = "Sebastian Enrico", email = "13523134@std.stei.itb.ac.id"}
]
dependencies = [
    "flet>=0.21.0",
    "mysql-connector-python>=8.0.33",
    "PyMuPDF>=1.23.0",
    "faker>=19.0.0"
]
requires-python = ">=3.9"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Manual Installation

Jika tidak menggunakan **uv**, install dependencies dengan pip:

```bash
pip install flet mysql-connector-python PyMuPDF faker
```

### Database MySQL

Pastikan Anda sudah menginstall MySQL Server dan buat database dengan nama tubes3_seeding:

```sql
CREATE DATABASE tubes3_seeding;
ALTER USER 'root'@'localhost' IDENTIFIED BY '12345';
FLUSH PRIVILEGES;
```

Konfigurasi database dapat disesuaikan di `db.py` dan `seeding.py` pada variabel `DB_CONFIG`.

Gunakan password 12345 dan gunakan username root

Dan anda bisa copas perintah yang ada di file database pada link di bawah

## 🚀 Cara Menjalankan Program

1. **Setup Database dan Seed Data (hanya jika anda ingin data baru)**
   Jalankan:

   ```bash
   python seeding.py
   ```

2. **Menjalankan Aplikasi GUI**
   Jalankan:

   ```bash
   python main.py
   ```

3. **Struktur Folder**

   ```
   data/
   |   └── [ROLE]/[pdfs]
   project/
   ├── main.py
   ├── utils/
   ├── algo/
   └── regex/
   ```

## 👨‍💻 Author

* Nama/NIM: **Abdullah Farhan/13523042**
* Nama/NIM: **William Andrian/13523006**
* Nama/NIM: **Sebastian Enrico/13523134**
* Kelompok: **\[Isi nama kelompok sesuai sheet]**

Link Database Dapat diakses pada: https://drive.google.com/file/d/12snp5U5Nfh0mHmPyAmyPoiICXvzUaJms/view 
---

Jika kamu ingin file ini disimpan langsung sebagai `README.md`, beritahu saja. Kalau sudah oke, saya bisa bantu lanjut generate `requirements.txt` atau file setup lainnya.

