import mysql.connector
from faker import Faker
import random
import os

# ---------- CONFIGURATION ----------

CVS_DIR = "../data/data"  # Root folder where roles and CVs are stored
NUM_APPLICANTS = 200

DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "12345",
    'database': "cv_ats_db"
}

# ---------- DATABASE SETUP ----------

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ApplicantProfile (
        applicant_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(50) DEFAULT NULL,
        last_name VARCHAR(50) DEFAULT NULL,
        date_of_birth DATE DEFAULT NULL,
        address VARCHAR(255) DEFAULT NULL,
        phone_number VARCHAR(20) DEFAULT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ApplicationDetail (
        detail_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        applicant_id INT NOT NULL,
        application_role VARCHAR(100) DEFAULT NULL,
        cv_path TEXT,
        FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)
            ON DELETE CASCADE
    );
    """)

    db.commit()
    cursor.close()
    db.close()
    print("Tables created successfully.")

# ---------- LOAD CVS STRUCTURE ----------

def load_cvs():
    role_to_cvs = {}
    for role in os.listdir(CVS_DIR):
        role_path = os.path.join(CVS_DIR, role)
        if os.path.isdir(role_path):
            pdfs = [
                os.path.join(role_path, f)
                for f in os.listdir(role_path)
                if f.lower().endswith('.pdf')
            ]
            if pdfs:
                role_to_cvs[role] = pdfs
    return role_to_cvs

# ---------- FAKE DATA INSERTION ----------

def insert_fake_data(num_applicants=NUM_APPLICANTS):
    fake = Faker()
    db = connect_db()
    cursor = db.cursor()

    # Load real CV paths from directory
    role_to_cvs = load_cvs()

    if not role_to_cvs:
        print("No valid CVs found in cvs/ directory.")
        return

    all_available_cvs = []
    for role, paths in role_to_cvs.items():
        # Only include .pdf files (case-insensitive)
        pdf_paths = [path for path in paths if path.lower().endswith('.pdf')]
        if pdf_paths:
            role_to_cvs[role] = pdf_paths
            for path in pdf_paths:
                all_available_cvs.append((role, path))
        else:
            role_to_cvs[role] = []

    used_cv_paths = set()

    for _ in range(num_applicants):
        # Insert applicant
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=60)
        address = fake.address().replace("\n", ", ")
        while True:
            phone = fake.phone_number()
            if len(phone) < 20:
                break

        cursor.execute("""
        INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, dob, address, phone))

        applicant_id = cursor.lastrowid

        # Assign 1–3 different roles with unique CVs
        available_roles = [r for r in role_to_cvs if role_to_cvs[r]]
        random.shuffle(available_roles)
        num_roles = min(random.randint(1, 3), len(available_roles))

        for role in available_roles[:num_roles]:
            # Filter unused CVs for this role
            unused_cvs = [cv for cv in role_to_cvs[role] if cv not in used_cv_paths]
            if not unused_cvs:
                continue

            full_cv_path = random.choice(unused_cvs)
            used_cv_paths.add(full_cv_path)

            # Extract only the filename
            filename_only = os.path.basename(full_cv_path)

            cursor.execute("""
            INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
            VALUES (%s, %s, %s)
            """, (applicant_id, role.capitalize().replace("-", " "), filename_only))

    db.commit()
    cursor.close()
    db.close()
    print(f"{num_applicants} applicants inserted with valid PDF CVs and roles.")

# ---------- MAIN EXECUTION ----------

if __name__ == "__main__":
    create_tables()
    insert_fake_data()