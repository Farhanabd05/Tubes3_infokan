import mysql.connector
from faker import Faker
import random
import os

# ---------- CONFIGURATION ----------

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

def setup_database_tables():
    database = establish_connection()
    cursor = database.cursor()

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

    database.commit()
    cursor.close()
    database.close()
    print("Tables created successfully.")

# ---------- LOAD CVS STRUCTURE ----------

def fetch_resume_files():
    position_to_resumes = {}
    for position in os.listdir(RESUME_DIRECTORY):
        position_directory = os.path.join(RESUME_DIRECTORY, position)
        if os.path.isdir(position_directory):
            pdf_files = [
                os.path.join(position_directory, file)
                for file in os.listdir(position_directory)
                if file.lower().endswith('.pdf')
            ]
            if pdf_files:
                position_to_resumes[position] = pdf_files
    return position_to_resumes

# ---------- FAKE DATA INSERTION ----------

def populate_sample_data(candidate_count=TOTAL_CANDIDATES):
    data_generator = Faker()
    database = establish_connection()
    cursor = database.cursor()

    # Load real CV paths from directory
    position_to_resumes = fetch_resume_files()

    if not position_to_resumes:
        print("No valid CVs found in data/ directory.")
        return

    complete_resume_list = []
    for job_position, file_paths in position_to_resumes.items():
        # Only include .pdf files (case-insensitive)
        pdf_file_paths = [file_path for file_path in file_paths if file_path.lower().endswith('.pdf')]
        if pdf_file_paths:
            position_to_resumes[job_position] = pdf_file_paths
            for file_path in pdf_file_paths:
                complete_resume_list.append((job_position, file_path))
        else:
            position_to_resumes[job_position] = []

    utilized_resume_paths = set()

    for _ in range(candidate_count):
        # Insert applicant
        candidate_first_name = data_generator.first_name()
        candidate_last_name = data_generator.last_name()
        birth_date = data_generator.date_of_birth(minimum_age=18, maximum_age=60)
        home_address = data_generator.address().replace("\n", ", ")
        while True:
            contact_number = data_generator.phone_number()
            if len(contact_number) < 20:
                break

        cursor.execute("""
        INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
        VALUES (%s, %s, %s, %s, %s)
        """, (candidate_first_name, candidate_last_name, birth_date, home_address, contact_number))

        current_applicant_id = cursor.lastrowid

        # Assign 1–3 different roles with unique CVs
        available_positions = [position for position in position_to_resumes if position_to_resumes[position]]
        random.shuffle(available_positions)
        selected_role_count = min(random.randint(1, 3), len(available_positions))

        for job_position in available_positions[:selected_role_count]:
            # Filter unused CVs for this role
            unused_resume_files = [resume_file for resume_file in position_to_resumes[job_position] if resume_file not in utilized_resume_paths]
            if not unused_resume_files:
                continue

            selected_resume_path = random.choice(unused_resume_files)
            utilized_resume_paths.add(selected_resume_path)

            # Extract only the filename
            resume_filename = os.path.basename(selected_resume_path)

            cursor.execute("""
            INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
            VALUES (%s, %s, %s)
            """, (current_applicant_id, job_position.capitalize().replace("-", " "), resume_filename))

    database.commit()
    cursor.close()
    database.close()
    print(f"{candidate_count} applicants inserted with valid PDF CVs and roles.")

# ---------- MAIN EXECUTION ----------

if __name__ == "__main__":
    setup_database_tables()
    populate_sample_data()