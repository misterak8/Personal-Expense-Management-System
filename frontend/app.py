import streamlit as st
from add_update import add_update_tab
from analytics_by_category import analytics_by_category_tab
from analytics_by_month import analytics_by_month_tab
from analytics_by_day_of_week import analytics_by_day_of_week_tab
from expenses_by_note import expenses_by_note_tab

# Page title
st.title("Expense Management System")

# Define 5 tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add/Update", "Analytics by Category",
"Analytics by Month", "Analytics by Day of Week", "Expenses by Note"])

with tab1:
    add_update_tab()

with tab2:
    analytics_by_category_tab()

with tab3:
    analytics_by_month_tab()

with tab4:
    analytics_by_day_of_week_tab()

with tab5:
    expenses_by_note_tab()
