import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def analytics_by_month_tab():
    st.title("Analytics by Month")

    # Input fields for year and category
    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("Year", min_value=2010, max_value=2070, value=2024, step=1)

    with col2:
        category = st.text_input(
            "Category (comma-separated or 'all')",
            value="all",
            help="Enter one or more categories separated by commas (e.g., 'Shopping, Misc') or 'all' to include all categories."
        )

    # Button to fetch analytics
    if st.button("Get Monthly Analytics"):
        # Prepare payload for the POST request
        payload = {
            "year": year,
            "category": category.strip()
        }

        # Make API request
        response = requests.post(f"{API_URL}/analytics/expenses/monthly", json=payload)

        if response.status_code == 200:
            # Parse response JSON
            response_data = response.json()

            # Prepare data for visualization
            data = {
                "Month": [item["month"] for item in response_data],
                "Total Amount": [item["total_amount"] for item in response_data]
            }

            df = pd.DataFrame(data)

            # Ensure months are sorted in ascending order from January to December
            month_order = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
            df_sorted = df.sort_values(by="Month")

            # Bar chart visualization
            st.title("Monthly Expense Breakdown")
            st.bar_chart(data=df_sorted.set_index("Month")["Total Amount"], width=0, height=0, use_container_width=True)

            # Format total amounts for display in table
            df_sorted["Total Amount"] = df_sorted["Total Amount"].map("{:.2f}".format)

            # Display table
            st.table(df_sorted)
        else:
            # Handle errors from the API
            error_message = response.json().get("detail", "An error occurred while fetching monthly analytics.")
            st.error(f"Error: {error_message}")
