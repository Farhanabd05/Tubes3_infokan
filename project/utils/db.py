# file: db.py
import mysql.connector
RESUME_DIRECTORY = "../data/data"  # Root folder where roles and CVs are stored
TOTAL_CANDIDATES = 200

DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "12345",
    'database': "cv_ats_db"
}

# ---------- DATABASE SETUP ----------

def establish_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_applicant_by_cv_filename(filename: str):
    conn = establish_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    query = """
    SELECT ap.applicant_id, ap.first_name, ap.last_name, ap.date_of_birth,
           ap.address, ap.phone_number, ad.application_role
    FROM ApplicantProfile ap
    JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
    WHERE ad.cv_path = %s
    """
    cursor.execute(query, (filename,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

if __name__ == "__main__":
    filename = "10554236.pdf"  # Ganti sesuai data kamu
    data = get_applicant_by_cv_filename(filename)
    if data:
        print("✅ Data ditemukan:")
        for k, v in data.items():
            print(f"{k}: {v}")
    else:
        print("❌ Tidak ada data dengan nama file tersebut.")
