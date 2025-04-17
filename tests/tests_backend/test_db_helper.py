import pytest
from backend import db_helper

def test_fetch_expenses_for_valid_date():
    expenses = db_helper.fetch_expenses_for_date("2024-08-24")

    assert len(expenses) == 7
    assert expenses[0]['amount'] == 1200
    assert "Broadband" in expenses[1]['notes'], f"Given word not in {expenses[1]['notes']}"

def test_fetch_expenses_for_invalid_date():

    expenses = db_helper.fetch_expenses_for_date("1824-08-24")
    assert len(expenses) == 0


def test_fetch_expense_summary_valid_date():
    expenses = db_helper.fetch_expense_summary("2024-08-24", "2024-08-26")
    assert len(expenses) == 6


def test_fetch_expense_summary_invalid_date():

    expenses = db_helper.fetch_expense_summary("2099-10-23", "2099-11-23")
    assert len(expenses) == 0


def test_fetch_expenses_for_valid_category_date():
    expenses = db_helper.fetch_expenses_for_particular_category_date("Utilities", "2024-08-24")

    assert len(expenses) > 0
    assert expenses[0]['category'].lower() == "utilities"


def test_fetch_expenses_for_invalid_category_date():
    # Test with an invalid category
    with pytest.raises(ValueError):
        db_helper.fetch_expenses_for_particular_category_date("Sports", "2024-08-24")

    # Test with an invalid date
    expenses = db_helper.fetch_expenses_for_particular_category_date("Shopping", "1824-08-24")
    assert len(expenses) == 0


def test_fetch_expenses_for_valid_note():
    # Assuming there are expenses with notes containing "EMI"
    expenses = db_helper.fetch_expenses_for_particular_note(year=2024, months=[8], wildcard_note="EMI")

    for item in expenses:
        if item['notes'] == "Motor Vehicle Insurance Premium":
            assert item['amount'] == 114

    for expense in expenses:
        assert "emi" in expense['notes'].lower()

def test_fetch_expenses_for_invalid_note():
    # Test with a note that doesn't exist in any expenses
    all_months = list(range(1, 13))  # [1, 2, 3, ..., 12]

    expenses = db_helper.fetch_expenses_for_particular_note(year=2024, months=all_months, wildcard_note="NonExistentNote")
    assert len(expenses) == 0


def test_fetch_expenses_by_category_and_day_valid():
    # Assuming there are expenses for 'Shopping' on weekdays
    expenses = db_helper.fetch_expenses_by_category_and_day("Shopping", "Weekday")

    assert len(expenses) > 0
    for expense in expenses:
        assert expense['category'].lower() == "shopping"
        # Verify that expense_date falls on a weekday
        weekday = expense['expense_date'].weekday()  # Python's datetime.weekday() returns 0 for Monday, 6 for Sunday
        assert weekday < 5


def test_fetch_expenses_by_category_and_day_invalid():
    # Test with an invalid category
    with pytest.raises(ValueError):
        db_helper.fetch_expenses_by_category_and_day("Sports", "Weekday")

    # Test with an invalid period
    with pytest.raises(ValueError):
        db_helper.fetch_expenses_by_category_and_day("Shopping", "Funday")

    # Test with a valid category but an invalid date (assuming no expenses on this date)
    expenses = db_helper.fetch_expenses_by_category_and_day("Debt Payment", "Sunday")
    assert len(expenses) == 0


def test_fetch_monthly_expenses_valid():
    # Assuming there are Food expenses for August 2024
    expenses = db_helper.fetch_monthly_expenses(2024, "Food")

    assert len(expenses) > 0

    assert expenses[7][0] == "August"
    assert expenses[7][1]  == 3642


    # Assuming there are expenses for the year 2024 in the categories "Misc" and "Shopping"
    expenses2 = db_helper.fetch_monthly_expenses(2024, "Misc, Shopping")

    assert len(expenses2) > 0

    assert expenses2[7][0] == "August"
    assert expenses2[7][1]  == 7997

def test_fetch_monthly_expenses_invalid():
    # Test with an invalid category
    with pytest.raises(ValueError):
        db_helper.fetch_monthly_expenses(2024, "Sports")

    # Test with a valid category but an invalid year
    expenses = db_helper.fetch_monthly_expenses(1824, "Entertainment")
    for i in range(len(expenses)):
        assert expenses[i][1] == 0







