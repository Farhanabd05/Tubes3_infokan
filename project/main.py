import flet as ft
import time
import sys
import os
import webbrowser
import re
import heapq

try:
    from algo.kmp import kmp_search
    from algo.bm import boyer_moore_search
    from algo.ahocor import AhoCorasick
    from algo.levenshtein import fuzzy_text_search
    from utils.pdf_to_text import load_all_cv_texts
    from utils.db import get_applicant_by_cv_filename
    from regex.extract_exp import extract_experience_section, extract_text_from_pdf
    from regex.extract_edu import extract_education_section
    from regex.extract_skill import extract_skills_from_resume
    from utils.seeding import setup_database_tables, populate_sample_data
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all required files (kmp.py, bm.py, etc.) are in their respective directories (algo/, utils/, etc.).")
    sys.exit(1)


# Load CV data once at the start
print("📄 Loading CVs from data/data ...")
try:
    # Adjust the path based on your project structure
    DUMMY_DATA = load_all_cv_texts("../data/data")
    print(f"✅ Loaded {len(DUMMY_DATA)} CVs.")
except FileNotFoundError:
    print("❌ Error: 'data/data' directory not found. Please check the path.")
    sys.exit(1)


def on_view_cv(path: str):
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        webbrowser.open(f"file://{abs_path}")
    else:
        print(f"❌ File not found: {abs_path}")

def main(page: ft.Page):
    page.title = "CV Analyzer App"
    page.padding = 20


    keywords_field = ft.TextField(
        hint_text="Enter keywords, e.g. React, Express, HTML",
        width=600,
        border_radius=ft.border_radius.all(20)
    )

    algo_dropdown = ft.Dropdown(
        label="Search Algorithm",
        width=200,
        border_radius=ft.border_radius.all(20),
        options=[
            ft.dropdown.Option("KMP"),
            ft.dropdown.Option("Boyer-Moore"),
            ft.dropdown.Option("Aho-Corasick")
        ],
        value="KMP"
    )

    top_matches = ft.Dropdown(
        label="Top Matches",
        width=100,
        border_radius=ft.border_radius.all(20),
        options=[ft.dropdown.Option(str(i)) for i in range (1, 120)],
        value="3"
    )

    fuzzy_matches_button = ft.ElevatedButton(
        text="Fuzzy Matches",
        visible=False,
        on_click=lambda e: show_fuzzy_matches_popup()
    )

    #Loading Animation
    loading_bar = ft.ProgressBar(width=400, visible=False)
    loading_text = ft.Text("Analyzing CVs...", visible=False, italic=True)
    loading_container = ft.Column([loading_text, loading_bar],
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                  spacing=10,
                                  visible=False)
    
    # Search Button
    search_button = ft.ElevatedButton(
        text="Search",
        width=150,
        on_click=on_search,
    )

    results_header = ft.Text("Results", size=18, weight=ft.FontWeight.BOLD)
    scan_info = ft.Text("Ready to search.", italic=True)
    results_container = ft.Column(spacing=15)


    fuzzy_match_results = {}
    matches = []

    def clear_fuzzy_results():
        nonlocal fuzzy_match_results
        fuzzy_match_results = {}

    def on_search(e):
        # 1. Show loading animation and disable search button
        loading_container.visible = True
        search_button.disabled = True
        results_container.visible = False
        scan_info.value = "Analyzing CVs..."
        page.update()

        # Small delay to ensure UI updates before blocking
        time.sleep(0.1)

        # 2. Run the core search logic
        _perform_search()

        # 3. Hide loading and show results
        loading_container.visible = False
        search_button.disabled = False
        results_container.visible = True
        page.update()

    def _perform_search():
        nonlocal matches, fuzzy_match_results
        t0_exact = time.time()
        keywords = [kw.strip().lower() for kw in (keywords_field.value or '').split(',') if kw.strip()]
        if not keywords:
            scan_info.value = "Please enter at least one keyword."
            results_container.controls.clear()
            results_container.controls.append(ft.Text("No keywords entered.", italic=True))
            return
            
        exact_matches = []

        if not hasattr(DUMMY_DATA[0], '_lower_text'):
            for data in DUMMY_DATA:
                data['_lower_text'] = data['text'].lower()

        search_func = kmp_search if algo_dropdown.value == "KMP" else boyer_moore_search
        aho = AhoCorasick(keywords) if algo_dropdown.value == "Aho-Corasick" else None

        for data in DUMMY_DATA:
            total_matches = 0
            details = []
            if aho:
                found_keywords = aho.search_all(data['_lower_text'])
                for kw, positions in found_keywords.items():
                    count = len(positions)
                    total_matches += count
                    details.append((kw, count))
            else:
                for kw in keywords:
                    positions = search_func(data['_lower_text'], kw.lower())
                    count = len(positions)
                    if count:
                        total_matches += count
                        details.append((kw, count))

            if total_matches:
                exact_matches.append((data, total_matches, details))

        exact_matches = heapq.nlargest(len(exact_matches), exact_matches, key=lambda x: x[1])
        
        top_n = int(top_matches.value or "3")
        
        if len(exact_matches) >= top_n:
            fuzzy_used = False
            fuzzy_ms = None
            final_matches = []
            for data, score, details in exact_matches[:top_n]:
                final_matches.append((data, score, details, "exact"))
            clear_fuzzy_results()
        else:
            fuzzy_used = True
            fuzzy_start = time.time()
            clear_fuzzy_results()
            
            exact_matches_lookup = {id(match_data): (match_score, match_details) 
                                    for match_data, match_score, match_details in exact_matches}
            
            combined_matches = []
            
            for data in DUMMY_DATA:
                exact_score, exact_details, exact_keywords_in_cv = (0, [], set())
                if id(data) in exact_matches_lookup:
                    exact_score, details_tuple = exact_matches_lookup[id(data)]
                    exact_details = list(details_tuple)
                    exact_keywords_in_cv = {kw for kw, _ in exact_details}

                fuzzy_score = 0
                fuzzy_details_list = []
                for kw in keywords:
                    if kw not in exact_keywords_in_cv:
                        count, matched_words = fuzzy_text_search(data['text'], kw)
                        if count > 0:
                            fuzzy_score += count
                            fuzzy_details_list.append((kw, count))
                            if kw not in fuzzy_match_results:
                                fuzzy_match_results[kw] = set()
                            fuzzy_match_results[kw].update(matched_words)

                if exact_score == 0 and fuzzy_score == 0:
                    continue

                match_type = "exact" if fuzzy_score == 0 else "fuzzy" if exact_score == 0 else "mixed"
                total_display_score = exact_score + fuzzy_score
                all_details = exact_details + fuzzy_details_list
                priority_score = exact_score * 1000 + fuzzy_score
                combined_matches.append((data, total_display_score, all_details, priority_score, match_type))

            for kw in fuzzy_match_results:
                if isinstance(fuzzy_match_results[kw], set):
                    fuzzy_match_results[kw] = list(fuzzy_match_results[kw])

            combined_matches = heapq.nlargest(len(combined_matches), combined_matches, key=lambda x: x[3])
            final_matches = [(data, score, details, match_type) 
                             for data, score, details, _, match_type in combined_matches[:top_n]]
            fuzzy_ms = int((time.time() - fuzzy_start) * 1000)

        # Update scan info
        exact_ms = int((time.time() - t0_exact) * 1000)
        total_found = len(final_matches)
        scan_info.value = f"Exact Match ({algo_dropdown.value}): {len(DUMMY_DATA)} CVs scanned in {exact_ms}ms\n"
        if fuzzy_used and fuzzy_ms is not None:
            scan_info.value += f"Fuzzy Match: Ran in {fuzzy_ms}ms\n"
        scan_info.value += f"Showing top {min(top_n, total_found)} of {total_found} matches"

        matches = final_matches
        fuzzy_matches_button.visible = fuzzy_used and bool(fuzzy_match_results)
        update_results_display()

    # Pagination 
    items_per_page = 8
    current_page = 1

    def update_results_display():
        nonlocal current_page
        results_container.controls.clear()
        if not matches:
            results_container.controls.append(ft.Text("No matches found.", italic=True))
            page.update()
            return

        total_pages = (len(matches) + items_per_page - 1) // items_per_page
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        current_matches = matches[start_idx:end_idx]

        cards_row = ft.Row(spacing=15, wrap=True, vertical_alignment=ft.CrossAxisAlignment.START)

        for i, (data, total, details, match_type) in enumerate(current_matches, start=start_idx + 1):
            filename = data.get('filename', 'Unknown')
            
            if match_type == "exact": bgcolor = "#2E7D32"
            elif match_type == "fuzzy": bgcolor = "#C62828"
            else: bgcolor = "#FF8F00"
            
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"#{i}", weight=ft.FontWeight.BOLD, color="white"),
                            bgcolor=ft.Colors.with_opacity(0.3, "black"), padding=5, border_radius=15,
                            width=50, height=30, alignment=ft.alignment.center
                        ),
                        ft.Text(filename, weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(
                            content=ft.Text(match_type.upper(), size=10, color="white", weight=ft.FontWeight.BOLD),
                            bgcolor=ft.Colors.with_opacity(0.3, "black"), padding=4, border_radius=8
                        )
                    ], spacing=10),
                    ft.Text(f"{round(total, 2)} match score", italic=True),
                    ft.Text("Matched keywords:"),
                    ft.Column([ft.Text(f"• {kw}: {score} occurrence{'s' if score > 1 else ''}") for kw, score in details]),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(text="Summary", on_click=lambda e, name=filename: show_summary_popup(page, name)),
                            ft.PopupMenuItem(text="View CV", on_click=lambda e, path=data['path']: on_view_cv(path)),
                            *([ft.PopupMenuItem(text="Fuzzy Details", on_click=lambda e, card_data=data: show_fuzzy_matches_popup(card_data))] if match_type in ["fuzzy", "mixed"] else [])
                        ],
                        icon=ft.Icons.MORE_VERT, tooltip="Actions"
                    )
                ]),
                padding=15, bgcolor=bgcolor, width=260, border_radius=10, ink=True,
            )
            cards_row.controls.append(card)
        results_container.controls.append(cards_row)

        if total_pages > 1:
            pagination_controls = ft.Row([
                ft.ElevatedButton(text="Previous", disabled=current_page == 1, on_click=lambda e: change_page(-1)),
                ft.Text(f"Page {current_page} of {total_pages}"),
                ft.ElevatedButton(text="Next", disabled=current_page == total_pages, on_click=lambda e: change_page(1))
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            results_container.controls.append(pagination_controls)

        page.update()

    def change_page(direction):
        nonlocal current_page
        total_pages = (len(matches) + items_per_page - 1) // items_per_page
        current_page += direction
        current_page = max(1, min(current_page, total_pages))
        update_results_display()

    filename_index = {cv["filename"]: cv for cv in DUMMY_DATA}

    def show_summary_popup(page, filename):
        data = get_applicant_by_cv_filename(filename)
        
        if data is None:
            dialog = ft.AlertDialog(title=ft.Text("Profile not found"))
        else:
            # Use index for O(1) lookup instead of O(n) search
            cv_data = filename_index.get(filename)
            full_cv_path = cv_data["path"] if cv_data else None
            if full_cv_path:
                print("if path exists:", os.path.exists(full_cv_path))
            print(f"Full CV Path: {full_cv_path}")


            # Create content list
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

    def show_fuzzy_matches_popup(card_data=None):
        if not fuzzy_match_results:
            return
        
        # Get fuzzy matches specific to this card
        card_fuzzy_matches = {}
        if card_data:
            for kw in fuzzy_match_results.keys():
                count, matched_words = fuzzy_text_search(card_data['text'], kw)
                if count > 0:
                    card_fuzzy_matches[kw] = list(matched_words)
        else:
            card_fuzzy_matches = fuzzy_match_results
            
        content_items = [ft.Text("Fuzzy Match Results:", weight=ft.FontWeight.BOLD, size=16)]
        
        for keyword, typos in card_fuzzy_matches.items():
            content_items.extend([
                ft.Divider(),
                ft.Text(f"Keyword: '{keyword}'", weight=ft.FontWeight.BOLD),
                ft.Text("Similar words found:", italic=True)
            ])
            
            typos_list = list(typos) if isinstance(typos, set) else typos
            for typo in typos_list[:10]:  # Show max 10 typos per keyword
                content_items.append(
                    ft.Container(
                        content=ft.Text(f"• {typo}", size=12),
                        padding=ft.padding.only(left=20, bottom=2),
                        bgcolor="lightyellow",
                        border_radius=3
                    )
                )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Fuzzy Matches Found"),
            content=ft.Column(
                content_items,
                height=400,
                scroll=ft.ScrollMode.AUTO
            ),
            on_dismiss=lambda e: print("Fuzzy matches dialog closed")
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Main content layout
    main_content = ft.Column([
        ft.Text("CV Analyzer App", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Column([keywords_field]),
            ft.Column([algo_dropdown]),
            ft.Column([top_matches]),
            ft.Column([search_button]),
            ft.Column([fuzzy_matches_button])
        ], alignment=ft.MainAxisAlignment.START, spacing=10),
        ft.Divider(),
        ft.Column([
            results_header,
            scan_info,
            loading_container,
            results_container
        ], spacing=10)
    ], spacing=20)

    scrollable_container = ft.Column(
        controls=[main_content], expand=True, scroll=ft.ScrollMode.AUTO
    )
    page.add(scrollable_container)
    page.update()

if __name__ == "__main__":
    # Optional: Setup DB and populate sample data on first run
    # print("Setting up database...")
    # setup_database_tables()
    # populate_sample_data()
    # print("Database setup complete.")
    ft.app(target=main)
