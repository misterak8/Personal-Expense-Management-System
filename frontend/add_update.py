import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

def add_update_tab():
    selected_date = st.date_input("Enter the date:", datetime(2024, 8, 1))

    # Fetch existing expenses for the selected date
    response = requests.get(f"{API_URL}/expenses/{selected_date}")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    # Display entry count and pagination info
    total_entries = len(existing_expenses)
    records_per_page = 5
    total_pages = max(1, (total_entries + records_per_page - 1) // records_per_page)

    st.write(f"**{total_entries} entries** (Page {min(st.session_state.get('page', 1), total_pages)} of {total_pages})")

    # Pagination controls
    col1, col2 = st.columns([1, 3])
    with col1:
        page_number = st.number_input(
            "Page Number",
            min_value=1,
            max_value=total_pages,
            value=1,
            key="page"
        )

    # Paginate expenses
    start_index = (page_number - 1) * records_per_page
    end_index = start_index + records_per_page
    paginated_expenses = existing_expenses[start_index:end_index]

    categories = [
        "Food", "Utilities", "Housing", "Transportation",
        "Insurance", "Medical", "Debt Payment", "Entertainment",
        "Misc", "Shopping"
    ]

    # Add New Expense checkbox (outside form)
    show_new_expense = st.checkbox("Add New Expense", value=False)

    with st.form(key="expense_form"):
        # Existing expenses table
        if paginated_expenses:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.subheader("Amount")
            with col2:
                st.subheader("Category")
            with col3:
                st.subheader("Notes")
            with col4:
                st.subheader("Delete")

        expenses_to_update = []
        new_expenses = []
        delete_flags = []

        # Display paginated existing expenses
        for i, expense in enumerate(paginated_expenses):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                original_amount = expense["amount"]
                amount_input = st.number_input(
                    label="Amount",
                    min_value=0.0,
                    step=1.0,
                    value=original_amount,
                    key=f"amount_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                original_category = expense["category"]
                category_input = st.selectbox(
                    label="Category",
                    options=categories,
                    index=categories.index(original_category) if original_category in categories else 0,
                    key=f"category_{i}",
                    label_visibility="collapsed"
                )
            with col3:
                original_notes = expense["notes"]
                notes_input = st.text_input(
                    label="Notes",
                    value=original_notes,
                    key=f"notes_{i}",
                    label_visibility="collapsed"
                )
            with col4:
                delete_checkbox = st.checkbox(
                    label="Delete",
                    key=f"delete_{i}",
                    value=False,
                    label_visibility="collapsed"
                )

            # Track changes and delete flags
            expenses_to_update.append({
                "old_expense_date": selected_date.isoformat(),
                "old_amount": original_amount,
                "old_category": original_category,
                "old_notes": original_notes,
                "new_expense_date": selected_date.isoformat(),
                "new_amount": amount_input,
                "new_category": category_input,
                "new_notes": notes_input.strip()
            })
            delete_flags.append(delete_checkbox)

        # New expense section
        if show_new_expense:
            st.subheader("New Expense Details")
            new_amount = st.number_input(
                label="Amount",
                min_value=1,
                step=1,
                format="%d",
                key="new_amount"
            )
            new_category = st.selectbox(
                label="Category",
                options=categories,
                key="new_category"
            )
            new_notes = st.text_input(
                label="Notes",
                key="new_notes"
            )

            if new_notes.strip():
                new_expenses.append({
                    "expense_date": selected_date.isoformat(),
                    "amount": float(new_amount),
                    "category": new_category,
                    "notes": new_notes.strip()
                })

        # Three separate action buttons
        col_add, col_del, col_mod = st.columns(3)
        with col_add:
            add_clicked = st.form_submit_button("Confirm record addition")
        with col_del:
            del_clicked = st.form_submit_button("Confirm record(s) deletion")
        with col_mod:
            mod_clicked = st.form_submit_button("Confirm record(s) modification")

        if add_clicked or del_clicked or mod_clicked:
            payload = {"updates": [], "additions": []}

            if add_clicked:
                # Handle additions
                valid_new = [
                    e for e in new_expenses
                    if e["amount"] >= 1 and e["notes"]
                ]
                if not valid_new:
                    st.error("No valid new expenses to add")
                    return
                payload["additions"] = valid_new

            elif del_clicked:
                # Handle deletions
                deletes = []
                for i, flag in enumerate(delete_flags):
                    if flag:
                        orig = expenses_to_update[i]
                        deletes.append({
                            **orig,
                            "new_amount": 0.0  # Mark for deletion
                        })
                if not deletes:
                    st.error("No records selected for deletion")
                    return
                payload["updates"] = deletes

            elif mod_clicked:
                # Handle modifications
                modifications = []
                for i, expense in enumerate(expenses_to_update):
                    if delete_flags[i]: continue  # Skip deletions
                    if (expense["new_amount"] != expense["old_amount"] or
                        expense["new_category"] != expense["old_category"] or
                        expense["new_notes"].lower() != expense["old_notes"].lower()):
                        modifications.append(expense)
                if not modifications:
                    st.error("No modifications detected")
                    return
                payload["updates"] = modifications

            # Send to backend
            response = requests.post(f"{API_URL}/expenses/update", json=payload)

            if response.status_code == 200:
                st.success("Operation completed successfully!")
                st.rerun()
            else:
                error_message = response.json().get("detail", "Operation failed")
                st.error(f"Error: {error_message}")
