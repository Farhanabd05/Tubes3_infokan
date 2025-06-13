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

        if not matches:
            # Mulai fuzzy match
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

            fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
            top_n = int(top_matches.value or "3")
            matches = fuzzy_matches[:top_n]

        duration_ms = int((time.time() - t0) * 1000)
        fuzzy_ms = int((time.time() - fuzzy_start) * 1000) if fuzzy_used else 0

        scan_info.value = f"{len(DUMMY_DATA)} CVs scanned in {duration_ms}ms\n"
        if fuzzy_used:
            scan_info.value += f"Fuzzy Match executed in {fuzzy_ms}ms"

        # Update UI
        results_container.controls.clear()
        for data, total, details in matches:
            filename = data.get('filename', 'Unknown')
            # print(f"🔍 Debug: Processing CV - filename: {filename}")
            
            lines = [
                ft.Text(filename, weight=ft.FontWeight.BOLD, size=16),
                ft.Text(f"{round(total, 2)} match score" if fuzzy_used else f"{int(total)} matches", italic=True),
                ft.Text("Matched keywords:"),
            ] + [
                ft.Text(f"{i+1}. {kw}: {round(score, 2)} similarity" if fuzzy_used else f"{i+1}. {kw}: {int(score)} occurrence{'s' if score>1 else ''}")
                for i, (kw, score) in enumerate(details)
            ] + [
                ft.Row([
                   ft.ElevatedButton(
                        text="Summary",
                        on_click=lambda e, name=filename: (print(f"🔍 Debug: Summary button clicked for: {name}"), show_summary_popup(page, name))[1]
                    ),
                    ft.ElevatedButton(
                        text="View CV",
                        on_click=lambda e, path=data['path']: on_view_cv(path)
                    )
                ], spacing=10)
            ]
            results_container.controls.append(
                ft.Container(
                    content=ft.Column(lines),
                    padding=10,
                    bgcolor="lightgray",
                    width=200
                )
            )

        page.update()
    def show_summary_popup(page, filename):
        # print(f"🔍 Debug: Summary button clicked for: {filename}")
        data = get_applicant_by_cv_filename(filename)
        # print(f"🔍 Debug: get_applicant_by_cv_filename returned: {data}")
        # print(f"🔍 Debug: Data type: {type(data)}")
        # print(f"🔍 Debug: Data keys: {data.keys() if data else 'None'}")

        if data is None:
            dialog = ft.AlertDialog(title=ft.Text("Profile not found"))
        else:
            dialog = ft.AlertDialog(
                title=ft.Text("Applicant Summary"),
                content=ft.Column([
                    ft.Text(f"Name: {data['first_name']} {data['last_name']}"),
                    ft.Text(f"Role: {data['application_role']}"),
                    ft.Text(f"Date of Birth: {data['date_of_birth']}"),
                    ft.Text(f"Address: {data['address']}"),
                    ft.Text(f"Phone: {data['phone_number']}"),
                ]),
                on_dismiss=lambda e: print("Dialog closed")
            )

        # ⬇️ Tambahkan dialog ke page.overlay agar muncul!
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
