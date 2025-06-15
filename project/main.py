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
from algo.levenshtein import levenshtein_distance, fuzzy_text_search
from utils.pdf_to_text import load_all_cv_texts
from utils.db import get_applicant_by_cv_filename
from regex.extract_exp import extract_experience_section
from regex.extract_exp import extract_text_from_pdf
from regex.extract_edu import extract_education_section
from regex.extract_skill import extract_skills_from_resume
import re
from utils.seeding import setup_database_tables, populate_sample_data
# Use heapq for more efficient top-N selection
import heapq

# Dummy data sesuai SQL schema (ApplicantProfile dan ApplicationDetail)
print("📄 Loading CVs from data/data ...")
DUMMY_DATA = load_all_cv_texts("../data")  # atau "../data/data" tergantung run location
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
        width=500,
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

    # Fuzzy Matches button (initially hidden)
    fuzzy_matches_button = ft.ElevatedButton(
        text="Fuzzy Matches",
        visible=False,
        on_click=lambda e: show_fuzzy_matches_popup()
    )

    # Store fuzzy match results for popup
    fuzzy_match_results = {}
        
    def clear_fuzzy_results():
        nonlocal fuzzy_match_results
        fuzzy_match_results = {}

    # Tombol Search
    search_button = ft.ElevatedButton(
        text="Search",
        width=200,
        on_click=lambda e: on_search(e),
    )

    # Header dan container hasil
    results_header = ft.Text("Results", size=18, weight=ft.FontWeight.BOLD)
    scan_info = ft.Text("0 CVs scanned in 0ms", italic=True)
    results_container = ft.Column(spacing=15)

    def on_search(e):
        # Mulai hitung waktu exact match
        t0_exact = time.time()
        keywords = [kw.strip().lower() for kw in (keywords_field.value or '').split(',') if kw.strip()]
        exact_matches = []
        
        # Pre-lowercase all CV texts once
        if not hasattr(DUMMY_DATA[0], '_lower_text'):
            for data in DUMMY_DATA:
                data['_lower_text'] = data['text'].lower()

        # PHASE 1: Exact match search
        search_func = kmp_search if algo_dropdown.value == "KMP" else boyer_moore_search
        
        for data in DUMMY_DATA:
            total_matches = 0
            details = []
            for kw in keywords:
                if algo_dropdown.value == "Aho-Corasick":
                    positions = AhoCorasick.search(data['text'].lower(), [kw.lower()])
                else:
                    positions = search_func(data['_lower_text'], kw.lower())
                count = len(positions)
                if count:
                    total_matches += count
                    details.append((kw, count))

            if total_matches:
                is_all_matched = len(details)==len(keywords)
                exact_matches.append((data, total_matches, details,is_all_matched))

        # Sort exact matches by score
        # Ensure all exact keywords are in the CV as highest priority
        exact_matches = heapq.nlargest(len(exact_matches), exact_matches, key=lambda x: 1000*x[3]+x[1])
        
        top_n = int(top_matches.value or "3")
        exact_ms = int((time.time() - t0_exact) * 1000)
        
        # DECISION POINT: Do we need fuzzy search?
        if len(exact_matches) >= top_n:
            # We have enough exact matches, no need for fuzzy search
            fuzzy_used = False
            fuzzy_ms = None
            
            # Just add match_type to exact matches
            final_matches = []
            for data, score, details, _ in exact_matches[:top_n]:
                final_matches.append((data, score, details, "exact"))
            
            clear_fuzzy_results()
            
        else:
            # We need fuzzy search to fill remaining slots
            fuzzy_used = True
            fuzzy_start = time.time()
            clear_fuzzy_results()
            
            # Create lookup for exact matches for efficiency
            exact_matches_lookup = {id(match_data): (match_score, match_details) 
                                for match_data, match_score, match_details in exact_matches}
            
            combined_matches = []
            
            # PHASE 2: Combined exact + fuzzy search
            for data in DUMMY_DATA:
                # Get exact match details if any
                if id(data) in exact_matches_lookup:
                    exact_score, exact_details = exact_matches_lookup[id(data)]
                    exact_details = list(exact_details)
                    exact_keywords_in_cv = {exact_kw for exact_kw, _ in exact_details}
                else:
                    exact_score = 0
                    exact_details = []
                    exact_keywords_in_cv = set()

                # Run fuzzy search only for keywords without exact matches
                fuzzy_score = 0
                fuzzy_details = []
                
                for kw in keywords:
                    if kw not in exact_keywords_in_cv:  # Only fuzzy search if no exact match
                        count, matched_words = fuzzy_text_search(data['text'], kw)
                        if count > 0:
                            fuzzy_score += count
                            fuzzy_details.append((kw, count))
                            # Store fuzzy match results for popup
                            if kw not in fuzzy_match_results:
                                fuzzy_match_results[kw] = set()
                            fuzzy_match_results[kw].update(matched_words)

                # Skip if no matches found
                if exact_score == 0 and fuzzy_score == 0:
                    continue

                # Determine match type
                if exact_score > 0 and fuzzy_score == 0:
                    match_type = "exact"
                elif exact_score == 0 and fuzzy_score > 0:
                    match_type = "fuzzy"
                else:
                    match_type = "mixed"
                
                # Combine results
                total_display_score = exact_score + fuzzy_score
                all_details = exact_details + fuzzy_details
                # Priority: exact_score * 1000 + fuzzy_score (exact matches first)
                
                priority_score = is_all_words_exact*10e6 + exact_score * 10e3 + fuzzy_score
                
                combined_matches.append((data, total_display_score, all_details, priority_score, match_type))

            # Convert fuzzy match results sets to lists for popup display
            for kw in fuzzy_match_results:
                if isinstance(fuzzy_match_results[kw], set):
                    fuzzy_match_results[kw] = list(fuzzy_match_results[kw])

            # Sort by priority score and take top N
            combined_matches = heapq.nlargest(len(combined_matches), combined_matches, key=lambda x: x[3])
            final_matches = [(data, score, details, match_type) 
                            for data, score, details, _, match_type in combined_matches[:top_n]]
            
            fuzzy_ms = int((time.time() - fuzzy_start) * 1000)

        # Update scan info
        total_found = len(final_matches)
        scan_info.value = f"Exact Match: {len(DUMMY_DATA)} CVs scanned in {exact_ms}ms\n"
        if fuzzy_used:
            scan_info.value += f"Fuzzy Match: {fuzzy_ms}ms\n"
        scan_info.value += f"Showing top {min(top_n, total_found)} of {total_found} matches"

        # Set matches for pagination
        matches = final_matches

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

            

            # Create row for cards only
            cards_row = ft.Row(spacing=15, vertical_alignment=ft.CrossAxisAlignment.START)
            
            for i, (data, total, details, match_type) in enumerate(current_matches, start_idx + 1):
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
                        ft.Text(filename, weight=ft.FontWeight.BOLD, size=16),
                        ft.Container(
                            content=ft.Text(match_type.upper(), size=10, color="white", weight=ft.FontWeight.BOLD),
                            bgcolor="gray",
                            padding=3,
                            border_radius=8
                        )
                    ], spacing=10),
                    ft.Text(f"{round(total, 2)} match score" if fuzzy_used else f"{int(total)} matches", italic=True),
                    ft.Text("Matched keywords:"),
                ] + [
                    ft.Text(f"• {kw}: {int(score)} match{'es' if score>1 else ''}" if fuzzy_used else f"• {kw}: {int(score)} occurrence{'s' if score>1 else ''}")
                    for kw, score in details
                ] + [
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                text="Summary",
                                on_click=lambda e, name=filename: show_summary_popup(page, name)
                            ),
                            ft.PopupMenuItem(
                                text="View CV", 
                                on_click=lambda e, path=data['path']: on_view_cv(path)
                            ),
                            *(
                                [ft.PopupMenuItem(
                                    text="Fuzzy Match",
                                    on_click=lambda e, card_data=data: show_fuzzy_matches_popup(card_data),
                                )] if fuzzy_used else []
                            ),
                        ],
                        icon=ft.Icons.MORE_VERT,
                        tooltip="Actions"
                    )
                ]
                # Different colors based on match type
                if match_type == "exact":
                    bgcolor = "#118911" if i == 1 else "#125612" if i <= 3 else "#083208"  # Green shades for exact
                elif match_type == "fuzzy":
                    bgcolor = "#D12D00" if i == 1 else "#9F0F2C" if i <= 3 else "#5A1111"  # Red shades for fuzzy
                else:  # mixed
                    bgcolor = "#FFD700" if i == 1 else "#FFA500" if i <= 3 else "#FF8C00"  # Orange shades for mixed
                cards_row.controls.append(
                    ft.Container(
                        content=ft.Column(lines),
                        padding=10,
                        bgcolor=bgcolor,
                        width=230,
                        border_radius=10
                    )
                )

            results_container.controls.append(cards_row)
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
            page.update()
        def change_page(direction):
            nonlocal current_page
            current_page += direction
            current_page = max(1, min(current_page, total_pages))
            update_results_display()
        # Show/hide fuzzy matches button
        fuzzy_matches_button.visible = fuzzy_used
        page.update()
        # Initial display
        update_results_display()
    # Add filename index at startup
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
                                padding=ft.padding.only(left=10, bottom=5,right=10),
                                border=ft.border.all(1, "gray"),
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
                            padding=ft.padding.only(left=10, bottom=5, right=10),
                            border=ft.border.all(1, "lightblue"),
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
                            padding=ft.padding.only(left=10, bottom=5,right=10),
                            border=ft.border.all(1, "lightgreen"),
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




    # Susun layout
    # Susun layout dalam scroll container
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
            results_container
        ], spacing=10)
    ], spacing=20)
    
    # Bungkus dalam Container dengan scroll
    scrollable_container = ft.Column(
        controls=[main_content],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    page.add(scrollable_container)

if __name__ == "__main__":
    # # 1) Setup DB dan isi data sampel MySQL
    # setup_database_tables()
    # populate_sample_data()

    # 2) Jalankan aplikasi Flet
    ft.app(target=main)

