import mysql.connector
import os
from dotenv import load_dotenv
from contextlib import contextmanager
#import logging_setup
from logging_setup import setup_logger, log_function_call

# Initialize the logger
logger = setup_logger(name='db_helper', log_file='backend_server_logs.log')

# Create decorator with configured logger
log = log_function_call(logger)

# Load environment variables from .env
load_dotenv()

@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor(dictionary=True)
    yield cursor
    if commit:
        connection.commit()
    print("Closing cursor")

    cursor.close()
    connection.close()

@log
def fetch_expenses_for_date(expense_date):
    #logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (expense_date,))
        expenses_for_date = cursor.fetchall()
        return expenses_for_date


@log
def fetch_monthly_expenses(year: int, category: str):
    """
    Fetch month-wise expenses for a specific year and category(ies).

    Args:
        year (int): The year to filter expenses by.
        category (str): The category(ies) to filter expenses by (case-insensitive).

    Returns:
        List[Tuple]: A list of tuples containing the month name and total amount.
    """
    allowed_categories = {
        "food", "utilities", "housing", "transportation", "insurance",
        "medical", "debt payment", "entertainment", "misc", "shopping", "all"
    }

    # Normalize category input
    category_lower = category.lower()

    # Validate category input
    if category_lower == "all":
        category_filter = ""
    else:
        categories = [c.strip().lower() for c in category_lower.split(",")]
        for cat in categories:
            if cat not in allowed_categories:
                raise ValueError(
                    f"Invalid category: '{cat}'. Must be one of: "
                    f"{', '.join([c.title() for c in allowed_categories if c != 'all'])} or 'all'"
                )
        category_filter = " OR ".join([f"LOWER(category) = '{cat}'" for cat in categories])

    # logger.info(f"fetch_monthly_expenses called with year={year}, category='{category}'")
    with get_db_cursor() as cursor:
        # Execute query with year and category filters
        if category_filter:
            query = f'''
                SELECT
                    MONTHNAME(expense_date) AS month_name,
                    SUM(amount) AS total_amount
                FROM
                    expenses
                WHERE
                    YEAR(expense_date) = %s AND ({category_filter})
                GROUP BY
                    MONTH(expense_date), MONTHNAME(expense_date)
                ORDER BY
                    MONTH(expense_date);
            '''
        else:
            query = '''
                SELECT
                    MONTHNAME(expense_date) AS month_name,
                    SUM(amount) AS total_amount
                FROM
                    expenses
                WHERE
                    YEAR(expense_date) = %s
                GROUP BY
                    MONTH(expense_date), MONTHNAME(expense_date)
                ORDER BY
                    MONTH(expense_date);
            '''

        cursor.execute(query, (year,))
        expenses_by_month = cursor.fetchall()

        # Initialize a dictionary to hold month-wise expenses
        month_expenses = {}

        # Populate month_expenses dictionary
        for expense in expenses_by_month:
            month_expenses[expense['month_name']] = expense['total_amount']

        # Create a list of tuples with month names and total amounts
        result = []
        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                       "November", "December"]

        # Loop through each month and append to result
        for month in month_names:
            if month in month_expenses:
                result.append((month, month_expenses[month]))
            else:
                result.append((month, 0.0))

        return result


@log
def insert_expense(expense_date, amount, category, notes):
    # Define allowed categories (case-insensitive)
    allowed_categories = {
        "food", "utilities", "housing", "transportation", "insurance", "medical",
        "debt payment", "entertainment", "misc", "shopping"
    }

    # Validate category input
    if category.lower() not in allowed_categories:
        raise ValueError(f"Invalid category: '{category}'. Must be one of: {', '.join(allowed_categories)}")

    #logger.info(f"insert_expense called with {expense_date}, {amount}, {category}, {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )

@log
def delete_expenses_for_date(expense_date):
    #logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))

@log
def fetch_expense_summary(start_date, end_date):
    #logger.info(f"fetch_expense_summary called with start_date={start_date}, end_date={end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category, SUM(amount) as Total
               FROM expenses WHERE expense_date
               BETWEEN %s and %s
               GROUP BY category;''',
            (start_date, end_date)
        )

        data = cursor.fetchall()
        return data

@log
def fetch_expenses_for_particular_category_date(category, expense_date):
    allowed_categories = {
        "food", "utilities", "housing", "transportation", "insurance",
        "medical", "debt payment", "entertainment", "misc", "shopping", "all"
    }

    # Normalize category input
    category_lower = category.lower()

    # Validate category
    if category_lower not in allowed_categories:
        raise ValueError(
            f"Invalid category: '{category}'. Must be one of: "
            f"{', '.join([c.title() for c in allowed_categories if c != 'all'])} or 'all'"
        )
    #logger.info(f"fetch_expenses_for_particular_category_date called with category='{category}', expense_date={expense_date}")
    with get_db_cursor() as cursor:
        if category_lower == "all":
            # Query without category filter
            cursor.execute(
                "SELECT * FROM expenses WHERE expense_date = %s",
                (expense_date,)
            )
        else:
            # Case-insensitive category match using LOWER()
            cursor.execute(
                "SELECT * FROM expenses "
                "WHERE expense_date = %s AND LOWER(category) = %s",
                (expense_date, category_lower)
            )

        expenses_for_category_date = cursor.fetchall()
        return expenses_for_category_date if expenses_for_category_date else []

@log
def fetch_expenses_for_particular_note(wildcard_note: str, year: int, months: list):
    """Fetch expenses matching note pattern, year, and months."""
    with get_db_cursor() as cursor:
        # Base query with new filters
        query = """
            SELECT * FROM expenses 
            WHERE LOWER(notes) LIKE %s 
            AND YEAR(expense_date) = %s 
            AND MONTH(expense_date) IN ({})
            ORDER BY expense_date DESC
        """.format(','.join(['%s'] * len(months)))  # Dynamic IN clause

        # Prepare parameters
        wildcard_term = '%' + wildcard_note.lower() + '%'
        params = [wildcard_term, year] + months

        cursor.execute(query, params)
        results = cursor.fetchall()
        return results if results else []

@log
def fetch_expenses_by_category_and_day(category: str, period_of_week: str):
    # Define allowed categories and periods
    allowed_categories = {
        "food", "utilities", "housing", "transportation", "insurance",
        "medical", "debt payment", "entertainment", "misc", "shopping", "all"
    }
    allowed_periods = {
        "weekend", "weekday",
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday"
    }

    # Normalize inputs
    period = period_of_week.lower()
    category_filter = category.lower()

    # Validate category
    if category_filter not in allowed_categories:
        valid_cats = [c.title() for c in allowed_categories if c != "all"]
        raise ValueError(
            f"Invalid category: '{category}'. Must be one of: "
            f"{', '.join(valid_cats)} or 'all'"
        )

    # Validate period
    if period not in allowed_periods:
        raise ValueError(
            f"Invalid period: '{period_of_week}'. Must be either: "
            "'weekend', 'weekday', or a day name (e.g. 'Monday')."
        )

    #logger.info(f"fetch_expenses_by_category_and_day called with category='{category}', period_of_week='{period_of_week}'")
    with get_db_cursor() as cursor:
        query = "SELECT * FROM expenses WHERE "
        conditions = []
        params = []

        # Category filter (skip if 'all')
        if category_filter != "all":
            conditions.append("LOWER(category) = %s")
            params.append(category_filter)

        # Period filter
        if period == "weekend":
            conditions.append("DAYOFWEEK(expense_date) IN (1,7)")  # Sun=1, Sat=7
        elif period == "weekday":
            conditions.append("DAYOFWEEK(expense_date) BETWEEN 2 AND 6")  # Mon-Fri
        else:  # Specific day
            conditions.append("LOWER(DAYNAME(expense_date)) = %s")
            params.append(period)

        # Build final query
        query += " AND ".join(conditions) + " ORDER BY expense_date DESC"

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        return results if results else []


@log
def delete_expense(expense_date: str, category: str, notes: str):
    """
    Deletes a record from the database based on expense_date, category, and notes.
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            DELETE FROM expenses 
            WHERE expense_date = %s 
            AND category = %s 
            AND LOWER(notes) = LOWER(%s)
            """,
            (expense_date, category, notes)
        )

@log
def add_expense(expense_date: str, amount: float, category: str, notes: str, check_duplicate: bool = False):
    with get_db_cursor(commit=True) as cursor:
        if check_duplicate:
            cursor.execute(
                """
                SELECT 1 FROM expenses 
                WHERE expense_date = %s 
                AND amount = %s 
                AND category = %s 
                AND LOWER(notes) = LOWER(%s)
                """,
                (expense_date, amount, category, notes)
            )
            if cursor.fetchone():
                raise ValueError("Duplicate expense entry")

        cursor.execute(
            """
            INSERT INTO expenses (expense_date, amount, category, notes)
            VALUES (%s, %s, %s, %s)
            """,
            (expense_date, amount, category, notes)
        )


def check_duplicate(expense_date: str, amount: float, category: str, notes: str, exclude_original: tuple = None):
    """Check for duplicates while optionally excluding original values"""
    with get_db_cursor() as cursor:
        query = """
            SELECT 1 FROM expenses 
            WHERE expense_date = %s 
            AND amount = %s 
            AND category = %s 
            AND LOWER(notes) = LOWER(%s)
        """
        params = [expense_date, amount, category, notes]

        if exclude_original:
            old_amount, old_category, old_notes = exclude_original
            query += " AND NOT (amount = %s AND category = %s AND LOWER(notes) = LOWER(%s))"
            params += [old_amount, old_category, old_notes]

        cursor.execute(query, params)
        return cursor.fetchone() is not None


def update_expense(old_data: dict, new_data: dict):
    """Atomic update operation with duplicate check"""
    with get_db_cursor(commit=True) as cursor:
        # 1. Check duplicate for new values (excluding original)
        cursor.execute(
            """
            SELECT 1 FROM expenses 
            WHERE expense_date = %s 
            AND amount = %s 
            AND category = %s 
            AND LOWER(notes) = LOWER(%s)
            AND NOT (amount = %s AND category = %s AND LOWER(notes) = LOWER(%s))
            """,
            (
                new_data["expense_date"],
                new_data["amount"],
                new_data["category"],
                new_data["notes"],
                old_data["amount"],
                old_data["category"],
                old_data["notes"]
            )
        )
        if cursor.fetchone():
            raise ValueError("Duplicate expense entry")

        # 2. Delete original
        cursor.execute(
            """
            DELETE FROM expenses 
            WHERE expense_date = %s 
            AND amount = %s 
            AND category = %s 
            AND LOWER(notes) = LOWER(%s)
            """,
            (
                old_data["expense_date"],
                old_data["amount"],
                old_data["category"],
                old_data["notes"]
            )
        )

        # 3. Insert new
        cursor.execute(
            """
            INSERT INTO expenses (expense_date, amount, category, notes)
            VALUES (%s, %s, %s, %s)
            """,
            (
                new_data["expense_date"],
                new_data["amount"],
                new_data["category"],
                new_data["notes"]
            )
        )

#if __name__ == "__main__":
#     pass

    #expenses = fetch_expenses_for_date("2024-08-30")
    #print(expenses)
    # expenses = fetch_expenses_for_particular_category_date("Shopping","2024-08-02")
    # for item in expenses:
    #     print(f"{item['category']} | {item['notes']} | {item['amount']}")

    # expenses = fetch_expenses_for_particular_note("bought")
    # for expense in expenses:
    #     print(f"id: {expense['id']}, "
    #           f"expense_date: {expense['expense_date'].isoformat()}, "
    #           f"amount: {expense['amount']:.2f}, "
    #           f"category: {expense['category']}, "
    #           f"notes: {expense['notes']}")

    # print(fetch_expenses_by_category_and_day("Shopping", "Monday"))


    #print(expenses)
    #insert_expense("2024-08-31", 20, "Food", "Drank juice")
    #delete_expenses_for_date("2024-08-28")
     # exp = fetch_expense_summary("2024-08-01", "2024-08-05")
     # for item in exp:
     #     print(f"{item['category']} : {item['Total']}")
    #
     #exp = fetch_expenses_for_date("2024-08-1")
     #print(exp)

    #expenses = fetch_monthly_expenses(year=2024, month="August")
    #print(expenses)

    #insert_expense("2024-08-01", 1200, "Insurance", "Health Insurance Premium")
    #exp = fetch_expenses_for_particular_category_date("Insurance", "2024-08-01")
    #print(exp)

    #exp = fetch_expenses_for_particular_note("Heal")
    #print(exp)

    #exp=fetch_expenses_by_category_and_day("misc","monday")
    #print(exp)

    #insert_expense("2024-08-01", 1800, "Bata", "Shoes")


    #exp = fetch_monthly_expenses(year=2024, category="food")
    #print(exp)

    # exp = fetch_expense_summary(start_date="2024-08-24", end_date="2024-08-26")
    # print(exp)

    #expenses = fetch_expenses_for_particular_note(year=2024,months=[8], wildcard_note="emI")
    #print(expenses)

    # Find all bill-related expenses from Q1 (Jan-Mar) 2024
    #result2 = fetch_expenses_for_particular_note("bill", 2024, [1, 2, 3])
    #print(result2)

    # Find all coffee expenses from 2024, all months
    #all_months = list(range(1, 13))  # [1, 2, 3, ..., 12]
    #result4 = fetch_expenses_for_particular_note("NotAnExpenseNote", 2024, all_months)
    #print(result4)

