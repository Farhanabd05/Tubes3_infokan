import flet as ft
import time
import sys
import os
# Add the parent directory (project/) to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.kmp import kmp_search

# Dummy data sesuai SQL schema (ApplicantProfile dan ApplicationDetail)
DUMMY_DATA = [
    { 'id': 1, 'name': 'Farhan', 'text': 'React Express HTML' },
    { 'id': 2, 'name': 'Aland',  'text': 'React Python'        },
    { 'id': 3, 'name': 'Ariel',  'text': 'Express Go'         },
    # Tambahkan lebih banyak dummy jika diperlukan
]

# UI Flet untuk CV Analyzer App

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
    algo_toggle = ft.Switch(value=True, label="Use KMP (off means BM)")

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
        # Mulai hitung waktu pencarian
        t0 = time.time()

        # Ambil dan bersihkan keywords
        keywords = [kw.strip() for kw in (keywords_field.value or '').split(',') if kw.strip()]
        matches = []

        # Cari setiap dummy record
        for data in DUMMY_DATA:
            total_matches = 0
            details = []
            for kw in keywords:
                # Pilih KMP atau BM (saat ini menggunakan KMP untuk keduanya)
                positions = kmp_search(data['text'].lower(), kw.lower())
                count = len(positions)
                if count:
                    total_matches += count
                    details.append((kw, count))
            if total_matches:
                matches.append((data, total_matches, details))

        # Urutkan dan ambil top N
        matches.sort(key=lambda x: x[1], reverse=True)
        top_n = int(top_matches.value or "3")
        matches = matches[:top_n]

        # Hitung durasi
        duration_ms = int((time.time() - t0) * 1000)
        scan_info.value = f"{len(DUMMY_DATA)} CVs scanned in {duration_ms}ms"

        # Update UI hasil
        results_container.controls.clear()
        for data, total, details in matches:
            lines = [
                ft.Text(data['name'], weight=ft.FontWeight.BOLD, size=16),
                ft.Text(f"{total} matches", italic=True),
                ft.Text("Matched keywords:"),
            ] + [
                ft.Text(f"{i+1}. {kw}: {cnt} occurrence{'s' if cnt>1 else ''}")
                for i, (kw, cnt) in enumerate(details)
            ] + [
                ft.Row([
                    ft.ElevatedButton(text="Summary"),
                    ft.ElevatedButton(text="View CV")
                ], spacing=10)
            ]
            card = ft.Container(
                content=ft.Column(lines),
                padding=10,
                bgcolor="lightgray",
                width=200
            )
            results_container.controls.append(card)

        page.update()

    # Susun layout
    page.add(
        ft.Text("CV Analyzer App", size=32, weight=ft.FontWeight.BOLD),
        ft.Column([
            ft.Text("Keywords:"), keywords_field,
            ft.Text("Search Algorithm:"), algo_toggle,
            top_matches, search_button
        ], spacing=10),
        results_header, scan_info, results_container
    )

# Jalankan Flet App
ft.app(target=main)
