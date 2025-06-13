# file: src/test_kmp_utils.py
import sys
import os
# Add the parent directory (project/) to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.seeding import establish_connection

def test_connection():
    try:
        conn = establish_connection()
        if conn.is_connected():
            print("✅ Koneksi ke database berhasil!")
        else:
            print("❌ Tidak berhasil terkoneksi ke database.")
        conn.close()
    except Exception as e:
        print(f"❌ Terjadi error saat menghubungkan ke database: {e}")

if __name__ == "__main__":
    test_connection()
