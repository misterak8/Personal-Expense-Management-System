<p align="center">
  <img src="https://img.icons8.com/ios-filled/200/4f46e5/wallet--v2.png" width="120" alt="Expense Management System" />
</p>

<h2 align="center">Expense Management System</h2>
<p align="center"><b>A modern app for tracking, analyzing, & managing your expenses.</b></p>

<p align="center">
  <a href="https://streamlit.io/"><img alt="Streamlit" src="https://img.shields.io/badge/streamlit-1.43.2-ff4b4b?logo=streamlit&logoColor=white"></a>
  <a href="https://pandas.pydata.org/"><img alt="Pandas" src="https://img.shields.io/badge/pandas-2.2.3-150458?logo=pandas&logoColor=white"></a>
  <a href="https://pytest.org/"><img alt="Pytest" src="https://img.shields.io/badge/pytest-8.3.5-0a9edc?logo=pytest&logoColor=white"></a>
  <a href="https://pydantic-docs.helpmanual.io/"><img alt="Pydantic" src="https://img.shields.io/badge/pydantic-2.10.6-008080?logo=pydantic&logoColor=white"></a>
  <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/fastapi-0.115.11-009688?logo=fastapi&logoColor=white"></a>
  <a href="https://www.uvicorn.org/"><img alt="Uvicorn" src="https://img.shields.io/badge/uvicorn-0.34.0-4f46e5?logo=uvicorn&logoColor=white"></a>
  <a href="https://requests.readthedocs.io/"><img alt="Requests" src="https://img.shields.io/badge/requests-2.32.3-20232a?logo=python&logoColor=white"></a>
  <a href="https://dev.mysql.com/doc/connector-python/en/"><img alt="MySQL Connector" src="https://img.shields.io/badge/mysql--connector--python-8.0.33-4479a1?logo=mysql&logoColor=white"></a>
  <a href="https://pypi.org/project/python-dotenv/"><img alt="python-dotenv" src="https://img.shields.io/badge/python--dotenv-1.0.1-44a833?logo=python&logoColor=white"></a>
</p>

<p align="center">
  <b>Backend:</b> FastAPI &nbsp; | &nbsp; <b>Frontend:</b> Streamlit &nbsp; | &nbsp; <b>Database:</b> MySQL
</p>

<p align="center">
  This project uses a MySQL database for persistent storage, FastAPI for the backend API server, & Streamlit for the interactive frontend interface.
</p>

---




A modern, full-stack web application for tracking, managing, & analyzing personal expenses. The application features a user-friendly interface, powerful analytics, robust data validation, & secure credential management.

---

## Features

- **Expense Management**: Add, update, & delete expenses with ease.
- **Pagination**: View expenses in manageable pages for each date.
- **Analytics by Category**: Visualize spending breakdowns by category for any time period.
- **Monthly Analytics**: Analyze expenses month-by-month for selected categories & years.
- **Day of Week Analytics**: Discover spending patterns by day of the week, weekdays, or weekends.
- **Search by Note**: Case-insensitive search for expenses by note, with year & month filters.
- **Data Validation**: Prevents duplicate entries, enforces valid categories, & ensures input correctness.
- **Secure Credentials**: Uses `python-dotenv` for secure database credential storage.
- **Logging**: All backend operations are logged for monitoring & debugging.
- **Sample Data Generation**: Easily populate your database with sample data for testing.

---

## Folder Structure

```
Project_Expense_Tracking_System/
│
├── backend/
│   ├── __init__.py
│   ├── backend_server.py         # FastAPI server implementation
│   ├── db_helper.py              # Database operations and utilities
│   ├── logging_setup.py          # Logging configuration and decorators
│   ├── insert_data_into_db.py    # Script for adding random/sample entries
│   └── .env                      # Environment variables (not in git)
│
├── frontend/
│   ├── __init__.py
│   ├── app.py                    # Main Streamlit application
│   ├── add_update.py             # Tab 1: Add/Update expenses
│   ├── analytics_by_category.py  # Tab 2: Category analytics
│   ├── analytics_by_month.py     # Tab 3: Monthly analytics
│   ├── analytics_by_day_of_week.py # Tab 4: Day of week analytics
│   └── expenses_by_note.py       # Tab 5: Search by note
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration for import paths
│   └── tests_backend/
│       ├── __init__.py
│       └── test_db_helper.py     # Tests for database functions
│
├── .gitignore                    # Git ignore file
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MySQL Server
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/expense-management-system.git
cd expense-management-system
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

1. Create a MySQL database named `expense_manager`.
2. Create a `.env` file in the `backend` directory with the following content (no quotes):

    ```
    DB_HOST=localhost
    DB_USER=your_mysql_username
    DB_PASSWORD=your_mysql_password
    DB_NAME=expense_manager
    ```

### 5. (Optional) Insert Sample Data

Populate the database with random sample data for testing:

```bash
python backend/insert_data_into_db.py
```

---

## Running the Application

### 1. Start the Backend Server

```bash
cd backend
uvicorn backend_server:app --reload
```

### 2. Start the Frontend Application

Open a new terminal, navigate to the project directory, & run:

```bash
cd frontend
streamlit run app.py
```

### 3. Access the Application

Open your browser and go to:

```
http://localhost:8501
```

---

## Tab Functionality

### **Tab 1: Add/Update**
- Fetches expenses for a specified date. Pagination is implemented (5 entries per page).
- Displays total entries & total pages for the selected date.
- **Add New Expense**: Check "Add New Expense", enter details, & click "Confirm record addition". Duplicate entries (same amount, category, notes for a date) are not allowed.
- **Modify Expense**: Edit existing entries & click "Confirm record(s) modification".
- **Delete Expense**: Select entries via checkboxes & click "Confirm record(s) deletion".

### **Tab 2: Analytics by Category**
- Provides an expense breakdown by category for a user-specified time period.
- Displays both a bar chart & a detailed table of totals & percentages.

### **Tab 3: Analytics by Month**
- Offers analytics by month for a selected year.
- User can specify one or more categories.
- Displays a monthly expense breakdown chart & table.

### **Tab 4: Analytics by Day of Week**
- Provides analytics by the chosen day of the week, or for all weekdays/weekends.
- User can select one or more categories.
- Results are sorted in descending order of expense amount.

### **Tab 5: Expenses by Note**
- Allows searching for expenses by any text in the note (case-insensitive, minimum 3 characters).
- User must specify the year & one or more months.
- Results are shown in descending order of date, with pagination (8 entries per page).

---

## Data Validation & Security

- **Duplicate Prevention**: No two records can have the same amount, category, & notes for a given date.
- **Category Restriction**: Only predefined categories can be selected; users cannot add new categories.
- **Input Validation**: All inputs are validated for correctness & completeness.
- **Credential Security**: All sensitive database credentials are stored in a `.env` file using `python-dotenv` & are not tracked by git.
- **Logging**: All backend operations are logged for monitoring & debugging.

---

## Sample Data Generation

- The script `backend/insert_data_into_db.py` allows you to quickly populate the database with a variety of random entries for testing & demonstration purposes.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## License

This project is licensed under the MIT License.


---

*Enjoy tracking & analyzing your expenses with the Expense Management System!*
