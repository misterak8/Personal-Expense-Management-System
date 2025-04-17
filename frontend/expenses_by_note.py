import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

API_URL = "http://localhost:8000"

def expenses_by_note_tab():
    st.title("Expenses by Note")

    # Initialize session state for pagination and data
    if 'note_page' not in st.session_state:
        st.session_state.note_page = 1
    if 'expenses_data' not in st.session_state:
        st.session_state.expenses_data = []

    # Input fields
    col1, col2 = st.columns(2)

    with col1:
        current_year = datetime.now().year
        year = st.number_input(
            "Year*",
            min_value=2020,
            max_value=2100,
            value=current_year,
            step=1
        )

    with col2:
        months = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December", "All"
        ]
        selected_months = st.multiselect(
            "Month(s)",
            options=months,
            default=["All"]
        )

        month_map = {month: idx + 1 for idx, month in enumerate(months[:12])}
        if "All" in selected_months:
            month_numbers = list(range(1, 13))
        else:
            month_numbers = [month_map[m] for m in selected_months if m != "All"]

    search_term = st.text_input("Search for expense by note (minimum 3 characters)")

    if st.button("Search"):
        # Reset pagination on new search
        st.session_state.note_page = 1

        # Validate inputs
        if not search_term.strip():
            st.error("Search term cannot be empty")
            return

        if len(search_term.strip()) < 3:
            st.error("Minimum 3 characters required for search")
            return

        if not re.match(r'^[a-zA-Z0-9 ]+$', search_term):
            st.error("Only letters, numbers, and spaces are allowed")
            return

        if re.sub(r'[\d ]', '', search_term) == '':
            st.error("Cannot search with numbers only")
            return

        try:
            # Send request to backend
            response = requests.post(
                f"{API_URL}/expenses/note",
                json={
                    "wildcard_note": search_term.strip(),
                    "year": year,
                    "months": month_numbers
                }
            )

            if response.status_code == 200:
                st.session_state.expenses_data = response.json()
            else:
                error_message = response.json().get("detail", "Failed to fetch data")
                st.error(f"Error: {error_message}")
                st.session_state.expenses_data = []

        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            st.session_state.expenses_data = []

    # Pagination controls
    if st.session_state.expenses_data:
        records_per_page = 8
        total_entries = len(st.session_state.expenses_data)
        total_pages = max(1, (total_entries + records_per_page - 1) // records_per_page)

        st.write(f"**{total_entries} entries** (Page {st.session_state.note_page} of {total_pages})")

        # Page navigation
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⏮ Previous"):
                if st.session_state.note_page > 1:
                    st.session_state.note_page -= 1
        with col_page:
            new_page = st.number_input(
                "Go to page",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.note_page,
                key="page_input"
            )
            if new_page != st.session_state.note_page:
                st.session_state.note_page = new_page
        with col_next:
            if st.button("Next ⏭"):
                if st.session_state.note_page < total_pages:
                    st.session_state.note_page += 1

        # Display current page results
        start_idx = (st.session_state.note_page - 1) * records_per_page
        end_idx = start_idx + records_per_page
        paginated_data = st.session_state.expenses_data[start_idx:end_idx]

        if paginated_data:
            df = pd.DataFrame(paginated_data)[['expense_date', 'category', 'amount', 'notes']]
            df['amount'] = df['amount'].map("{:.2f}".format)
            st.table(df)
        else:
            st.info("No entries found on this page")
    elif st.session_state.expenses_data == []:
        st.info("No expenses found matching the criteria")
