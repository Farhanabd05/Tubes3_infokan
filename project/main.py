import flet as ft

# Sesuai Spesifikasi Wajib: UI Flet untuk input keyword, pilihan algoritma, Top Matches, dan tampilan hasil (Spesifikasi Wajib poin UI) fileciteturn2file12

def main(page: ft.Page):
    page.title = "CV Analyzer App"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20

    # Input Keywords
    keywords_field = ft.TextField(
        hint_text="Enter keywords, e.g. React, Express, HTML",
        width=600
    )

    # Pilihan Algoritma Exact Match
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

    # Hasil
    results_header = ft.Text("Results", size=24, weight=ft.FontWeight.BOLD)
    scan_info = ft.Text("0 CVs scanned in 0ms", italic=True)
    results_container = ft.Row(spacing=20)

    
    def on_search(e):
        # Placeholder: implement logic search, kemudian update scan_info dan results_container
        scan_info.value = "100 CVs scanned in 100ms"
        # Contoh card
        card = ft.Container(
            content=ft.Column([
                ft.Text("Farhan", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("4 matches", italic=True),
                ft.Text("Matched keywords:"),
                ft.Text("1. React: 1 occurrence"),
                ft.Text("2. Express: 2 occurrences"),
                ft.Text("3. HTML: 1 occurrence"),
                ft.Row([
                    ft.ElevatedButton(text="Summary"),
                    ft.ElevatedButton(text="View CV")
                ], spacing=10)
            ]),
            padding=10,
            bgcolor="lightgray",
            width=200
        )
        results_container.controls.clear()
        results_container.controls.append(card)
        page.update()

    # Layout
    page.add(
        ft.Text("CV Analyzer App", size=32, weight=ft.FontWeight.BOLD),
        ft.Column([
            ft.Text("Keywords:"),
            keywords_field,
            ft.Text("Search Algorithm:"),
            algo_toggle,
            top_matches,
            search_button,
        ], spacing=10),
        results_header,
        scan_info,
        results_container
    )

ft.app(target=main)
