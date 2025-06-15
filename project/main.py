import flet as ft
import time
import sys
import os
import webbrowser

# Add the parent directory (project/) to Python path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.kmp import kmp_search
from algo.bm import boyer_moore_search
from algo.ahocor import AhoCorasick
from algo.levenshtein import levenshtein_distance
from utils.pdf_to_text import load_all_cv_texts
from utils.db import get_applicant_by_cv_filename
from regex.extract_exp import extract_experience_section
from regex.extract_exp import extract_text_from_pdf
from regex.extract_edu import extract_education_section
from regex.extract_skill import extract_skills_from_resume
import re
from utils.seeding import setup_database_tables, populate_sample_data


# Dummy data sesuai SQL schema (ApplicantProfile dan ApplicationDetail)
print("📄 Loading CVs from data/data ...")
DUMMY_DATA = load_all_cv_texts("../data/data")  # atau "../data/data" tergantung run location
print(f"✅ Loaded {len(DUMMY_DATA)} CVs.")

# UI Flet untuk CV Analyzer App

def on_view_cv(path: str):
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        webbrowser.open(f"file://{abs_path}")
    else:
        print(f"❌ File not found: {abs_path}")

def main(page: ft.Page):
    page.title = "CV Analyzer App"
    page.padding = 20
    
    # Input Keywords
    keywords_field = ft.TextField(
        hint_text="Enter keywords, e.g. React, Express, HTML",
        width=600,
        border_radius=ft.border_radius.all(20)
    )

    # Pilihan Algoritma Exact Match (KMP/BM)
    algo_dropdown = ft.Dropdown(
        label="Search Algorithm",
        width=200,
        border_radius=ft.border_radius.all(20),
        options=[
            ft.dropdown.Option("KMP"),
            ft.dropdown.Option("Boyer-Moore"),
            ft.dropdown.Option("Aho-Corasick")
        ],
        value="KMP"  # nilai default agar selalu ada pilihan
    )

    # Top Matches dropdown
    top_matches = ft.Dropdown(
        label="Top Matches",
        width=100,
        border_radius=ft.border_radius.all(20),
        options=[ft.dropdown.Option(str(i)) for i in range(1, 102)],
        value="3"
    )

    # Tombol Search
    search_button = ft.ElevatedButton(
        text="Search",
        width=600-200-100-12,
        on_click=lambda e: on_search(e),
    )

    # Header dan container hasil
    results_header = ft.Text("Results", size=18, weight=ft.FontWeight.BOLD)
    scan_info = ft.Text("0 CVs scanned in 0ms", italic=True)
    results_container = ft.Column(spacing=20)

    def on_search(e):
        # Mulai hitung waktu exact match
        t0_exact = time.time()
        keywords = [kw.strip() for kw in (keywords_field.value or '').split(',') if kw.strip()]
        matches = []
        fuzzy_used = False
        fuzzy_start = 0

        # Exact match dengan KMP
        for data in DUMMY_DATA:
            total_matches = 0
            details = []
            for kw in keywords: 
                if algo_dropdown.value == "KMP":
                    positions = kmp_search(data['text'].lower(), kw.lower())
                elif algo_dropdown.value == "Boyer-Moore":
                    positions = boyer_moore_search(data['text'].lower(), kw.lower())
                elif algo_dropdown.value == "Aho-Corasick":
                    ac = AhoCorasick([kw])
                    positions = ac.search(data['text'].lower(), [kw.lower()])
                count = len(positions)
                if count:
                    total_matches += count
                    details.append((kw, count))

            if total_matches:
                matches.append((data, total_matches, details))

        # Sort exact matches berdasarkan total_matches (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Ambil top N untuk exact matches
        top_n = int(top_matches.value or "3")
        
        if matches:
            # Jika ada exact matches, ambil top N
            matches = matches[:top_n]
        else:
            # Mulai fuzzy match jika tidak ada exact matches
            fuzzy_used = True
            # Waktu mulai fuzzy
            fuzzy_start = time.time()
            fuzzy_matches = []

            for data in DUMMY_DATA:
                score = 0
                details = []
                for kw in keywords:
                    words = data['text'].lower().split()
                    min_dist = min((levenshtein_distance(kw.lower(), word) for word in words), default=99)
                    similarity = 1 - min_dist / max(len(kw), 1)
                    if similarity >= 0.7:  # Threshold kemiripan (bisa diubah)
                        score += similarity
                        details.append((kw, similarity))

                if score > 0:
                    fuzzy_matches.append((data, score, details))

            # Sort fuzzy matches berdasarkan score (descending)
            fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
            
            # Ambil top N untuk fuzzy matches
            matches = fuzzy_matches[:top_n]

        # Hitung durasi exact dan fuzzy
        exact_ms = int(( (time.time() if not fuzzy_used else fuzzy_start) - t0_exact ) * 1000)
        fuzzy_ms = int((time.time() - fuzzy_start) * 1000) if fuzzy_used else None

        # Update scan info dengan informasi top matches
        total_found = len(matches)
        scan_info.value = f"Exact Match: {len(DUMMY_DATA)} CVs scanned in {exact_ms}ms\n"
        if fuzzy_used:
            scan_info.value += f"Fuzzy Match: {fuzzy_ms}ms\n"
        scan_info.value += f"Showing top {min(top_n, total_found)} of {total_found} matches"

            # Pagination variables
        items_per_page = 5
        current_page = 1
        total_pages = (len(matches) + items_per_page - 1) // items_per_page if matches else 1

        def update_results_display():
            # Update UI
            results_container.controls.clear()
            start_idx = (current_page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            current_matches = matches[start_idx:end_idx]

            # Add pagination controls below cards
            if total_pages > 1:
                pagination_controls = ft.Row([
                    ft.ElevatedButton(
                        text="Previous",
                        disabled=current_page == 1,
                        on_click=lambda e: change_page(-1)
                    ),
                    ft.Text(f"Page {current_page} of {total_pages}"),
                    ft.ElevatedButton(
                        text="Next", 
                        disabled=current_page == total_pages,
                        on_click=lambda e: change_page(1)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                
                results_container.controls.append(pagination_controls)

            # Create row for cards only
            cards_row = ft.Row(spacing=20, vertical_alignment=ft.CrossAxisAlignment.START)
            
            for i, (data, total, details) in enumerate(current_matches, start_idx + 1):
                # ... existing card creation code ...
                filename = data.get('filename', 'Unknown')
                lines = [
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"#{i}", weight=ft.FontWeight.BOLD, color="white"),
                            bgcolor="blue",
                            padding=5,
                            border_radius=15,
                            width=50,
                            height=30,
                            alignment=ft.alignment.center
                        ),
                        ft.Text(filename, weight=ft.FontWeight.BOLD, size=16)
                    ], spacing=10),
                    ft.Text(f"{round(total, 2)} match score" if fuzzy_used else f"{int(total)} matches", italic=True),
                    ft.Text("Matched keywords:"),
                ] + [
                    ft.Text(f"• {kw}: {round(score, 2)} similarity" if fuzzy_used else f"• {kw}: {int(score)} occurrence{'s' if score>1 else ''}")
                    for kw, score in details
                ] + [
                    ft.Row([
                    ft.ElevatedButton(
                            text="Summary",
                            on_click=lambda e, name=filename: show_summary_popup(page, name)
                        ),
                        ft.ElevatedButton(
                            text="View CV",
                            on_click=lambda e, path=data['path']: on_view_cv(path)
                        )
                    ], spacing=10)
                ]
                bgcolor = "green" if i == 1 else "#DA686C" if i <= 3 else "#3773FF"
                cards_row.controls.append(
                    ft.Container(
                        content=ft.Column(lines),
                        padding=10,
                        bgcolor=bgcolor,
                        width=200,
                        border_radius=10
                    )
                )

            results_container.controls.append(cards_row)
            page.update()
        def change_page(direction):
            nonlocal current_page
            current_page += direction
            current_page = max(1, min(current_page, total_pages))
            update_results_display()

        # Initial display
        update_results_display()
    def show_summary_popup(page, filename):
        data = get_applicant_by_cv_filename(filename)
        
        if data is None:
            dialog = ft.AlertDialog(title=ft.Text("Profile not found"))
        else:
            full_cv_path = None
            for cv in DUMMY_DATA:
                if cv["filename"] == filename:
                    full_cv_path = cv["path"]
                    print("if path exists:", os.path.exists(full_cv_path))
                    break
            print(f"Full CV Path: {full_cv_path}")


            # Create content list starting with basic info
            content_items = [
                ft.Text(f"Name: {data['first_name']} {data['last_name']}"),
                ft.Text(f"Role: {data['application_role']}"),
                ft.Text(f"Date of Birth: {data['date_of_birth']}"),
                ft.Text(f"Address: {data['address']}"),
                ft.Text(f"Phone: {data['phone_number']}"),
                ft.Divider(),
                ft.Text("Work Experience:", weight=ft.FontWeight.BOLD),
            ]
            # Jika file ditemukan, ekstrak pengalaman
            # Jika file ditemukan, ekstrak pengalaman dan education
            if full_cv_path and os.path.exists(full_cv_path):
                text = extract_text_from_pdf(full_cv_path)
                experiences = extract_experience_section(text)
                education = extract_education_section(text)
                skills = extract_skills_from_resume(text)
                # print("text:", text)
                # print("experiences:", experiences)
                # print("education:", education)
                # print("skills:", skills)
                # Add experience entries
                if experiences:
                    for i, exp in enumerate(experiences, 1):    
                        content_items.append(
                            ft.Container(
                                content=ft.Text(f"{i}. {exp}", size=12),
                                padding=ft.padding.only(left=10, bottom=5),
                                bgcolor="grey",
                                border_radius=5
                            )
                        )
                else:
                    content_items.append(ft.Text("No work experience found", italic=True))
                
                # Add education section
                content_items.extend([
                    ft.Divider(),
                    ft.Text("Education:", weight=ft.FontWeight.BOLD),
                ])
                
                if education:
                    content_items.append(
                        ft.Container(
                            content=ft.Text(education, size=12),
                            padding=ft.padding.only(left=10, bottom=5),
                            bgcolor="lightblue",
                            border_radius=5
                        )
                    )
                else:
                    content_items.append(ft.Text("No education information found", italic=True))
                
                # Add skills section
                content_items.extend([
                    ft.Divider(),
                    ft.Text("Skills:", weight=ft.FontWeight.BOLD),
                ])
                
                if skills:
                    content_items.append(
                        ft.Container(
                            content=ft.Text(skills, size=12),
                            padding=ft.padding.only(left=10, bottom=5),
                            bgcolor="lightgreen",
                            border_radius=5
                        )
                    )
                else:
                    content_items.append(ft.Text("No skills information found", italic=True))
            
            dialog = ft.AlertDialog(
                title=ft.Text("Applicant Summary"),
                content=ft.Column(
                    content_items,
                    height=400,
                    scroll=ft.ScrollMode.AUTO
                ),
                on_dismiss=lambda e: print("Dialog closed")
            )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()




    # Susun layout
    # Susun layout dalam scroll container
    main_content = ft.Column([
        ft.Text("CV Analyzer App", size=18, weight=ft.FontWeight.BOLD),
        ft.Column([
            ft.Text("Keywords:"), keywords_field,
                ft.Row([
                algo_dropdown,
                top_matches, 
                search_button
            ], spacing=10)
        ], spacing=10),
        results_header, scan_info, results_container
    ], spacing=20)

    # Bungkus dalam Container dengan scroll
    scrollable_container = ft.Column(
        controls=[main_content],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    page.add(scrollable_container)

if __name__ == "__main__":
    # 1) Setup DB dan isi data sampel MySQL
    setup_database_tables()
    populate_sample_data()

    # 2) Jalankan aplikasi Flet
    ft.app(target=main)

