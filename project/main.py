import flet as ft
import time
import sys
import os
import webbrowser

# Add the parent directory (project/) to Python path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.kmp import kmp_search
from algo.bm import boyer_moore_search
from algo.levenshtein import levenshtein_distance
from utils.pdf_to_text import load_all_cv_texts
from utils.db import get_applicant_by_cv_filename
from regex.extract_exp import extract_experience_section
from regex.extract_exp import extract_text_from_pdf
import re

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
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20

    # Input Keywords
    keywords_field = ft.TextField(
        hint_text="Enter keywords, e.g. React, Express, HTML",
        width=600
    )

    # Pilihan Algoritma Exact Match (KMP/BM)
    algo_dropdown = ft.Dropdown(
        label="Search Algorithm",
        width=200,
        options=[
            ft.dropdown.Option("KMP"),
            ft.dropdown.Option("Boyer-Moore")
        ],
    )

    # Top Matches dropdown
    top_matches = ft.Dropdown(
        label="Top Matches",
        width=100,
        options=[ft.dropdown.Option(str(i)) for i in range(1, 11)],
        value="3"
    )

    # Tombol Search
    search_button = ft.ElevatedButton(
        text="Search",
        width=600,
        on_click=lambda e: on_search(e)
    )

    # Header dan container hasil
    results_header = ft.Text("Results", size=24, weight=ft.FontWeight.BOLD)
    scan_info = ft.Text("0 CVs scanned in 0ms", italic=True)
    results_container = ft.Row(spacing=20)

    def on_search(e):
        t0 = time.time()
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

        duration_ms = int((time.time() - t0) * 1000)
        fuzzy_ms = int((time.time() - fuzzy_start) * 1000) if fuzzy_used else 0

        # Update scan info dengan informasi top matches
        total_found = len(matches)
        scan_info.value = f"{len(DUMMY_DATA)} CVs scanned in {duration_ms}ms\n"
        scan_info.value += f"Showing top {min(top_n, total_found)} of {total_found} matches\n"
        if fuzzy_used:
            scan_info.value += f"Fuzzy Match executed in {fuzzy_ms}ms"

        # Update UI
        results_container.controls.clear()
        for i, (data, total, details) in enumerate(matches, 1):
            filename = data.get('filename', 'Unknown')
            
            # Tambahkan ranking number
            lines = [
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"#{i}", weight=ft.FontWeight.BOLD, color="white"),
                        bgcolor="blue",
                        padding=5,
                        border_radius=15,
                        width=30,
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
            # Warna berbeda untuk ranking
            bgcolor = "green" if i == 1 else "lightblue" if i <= 3 else "lightgray"
            
            results_container.controls.append(
                ft.Container(
                    content=ft.Column(lines),
                    padding=10,
                    bgcolor=bgcolor,
                    width=200,
                    border_radius=10
                )
            )

        page.update()
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
            if full_cv_path and os.path.exists(full_cv_path):
                text = extract_text_from_pdf(full_cv_path)
                experiences = extract_experience_section(text)
                print("text:", text)
                print("experiences:", experiences)
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
    page.add(
        ft.Text("CV Analyzer App", size=32, weight=ft.FontWeight.BOLD),
        ft.Column([
            ft.Text("Keywords:"), keywords_field,
            algo_dropdown,
            top_matches, search_button
        ], spacing=10),
        results_header, scan_info, results_container
    )

# Jalankan Flet App
ft.app(target=main)
