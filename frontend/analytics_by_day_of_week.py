import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def analytics_by_day_of_week_tab():
    st.title("Analytics by Day of Week")

    # Input fields
    col1, col2 = st.columns(2)

    with col1:
        # Category selection
        categories = [
            "Food", "Utilities", "Housing", "Transportation",
            "Insurance", "Medical", "Debt Payment", "Entertainment",
            "Misc", "Shopping", "all"
        ]

        # Multi-select dropdown with validation for 'all'
        selected_categories = st.multiselect(
            "Select Categories",
            options=categories,
            default=["all"]
        )

        if "all" in selected_categories and len(selected_categories) > 1:
            st.error(
                "You cannot select 'all' along with other categories. Please unselect 'all' to choose specific categories.")
            return

    with col2:
        # Period selection with backend-compatible values
        period_map = {
            "Monday": "monday",
            "Tuesday": "tuesday",
            "Wednesday": "wednesday",
            "Thursday": "thursday",
            "Friday": "friday",
            "Saturday": "saturday",
            "Sunday": "sunday",
            "Weekdays": "weekday",
            "Weekends": "weekend"
        }
        selected_period = st.selectbox(
            "Select Period",
            options=list(period_map.keys())
        )

    if st.button("Generate Report"):
        if not selected_categories:
            st.error("Please select at least one category")
            return

        # Handle category selection
        if "all" in selected_categories:
            categories_to_process = ["all"]
        else:
            categories_to_process = selected_categories

        all_expenses = []

        try:
            backend_period = period_map[selected_period]

            # Process each category separately
            for category in categories_to_process:
                response = requests.post(
                    f"{API_URL}/expenses/category/period",
                    json={
                        "category": category.lower(),
                        "period_of_week": backend_period
                    }
                )

                if response.status_code == 200:
                    all_expenses.extend(response.json())
                else:
                    error_message = response.json().get("detail", "Failed to fetch data")
                    st.error(f"Error: {error_message}")
                    return

            if not all_expenses:
                st.info("No expenses found for the selected criteria")
                return

            # Aggregate and sort data
            df = pd.DataFrame(all_expenses)
            df['amount'] = df['amount'].astype(float)
            category_totals = df.groupby('category')['amount'].sum().reset_index()
            category_totals.columns = ['Category', 'Total Amount']

            # Sort by Total Amount (descending) before formatting
            category_totals = category_totals.sort_values(by='Total Amount', ascending=False)

            # Format to one decimal place
            category_totals['Total Amount'] = category_totals['Total Amount'].map(lambda x: f"{x:.1f}")

            # Display results
            st.table(category_totals)

        except Exception as e:
            st.error(f"Connection error: {str(e)}")
