from fastapi import FastAPI, HTTPException
from datetime import datetime, date
import db_helper
from typing import List
from pydantic import BaseModel, validator

class Expense(BaseModel):
    expense_date: date
    amount: float
    category: str
    notes: str

# Define request model for year and category
class MonthlyExpenseCategoryRequest(BaseModel):
    year: int
    category: str

class NoteRequest(BaseModel):
    wildcard_note: str
    year: int
    months: List[int]

class DateRange(BaseModel):
    start_date: date
    end_date: date

# Define request model for category and date
class CategoryDateRequest(BaseModel):
    category: str
    expense_date: date

# Define request model for category and period
class CategoryPeriodRequest(BaseModel):
    category: str
    period_of_week: str

class ExpenseUpdate(BaseModel):
    old_expense_date: str
    old_amount: float
    old_category: str
    old_notes: str
    new_expense_date: str
    new_amount: float
    new_category: str
    new_notes: str

class ExpenseAddition(BaseModel):
    expense_date: str
    amount: float
    category: str
    notes: str

class UpdateRequest(BaseModel):
    updates: List[ExpenseUpdate]
    additions: List[ExpenseAddition]


app=FastAPI()

@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: str):
    try:
        expense_date_obj = datetime.strptime(expense_date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

    expenses = db_helper.fetch_expenses_for_date(expense_date_obj)

    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses for the given date from the database")

    return expenses

@app.post("/expenses/addorudpate/")
def add_or_update_expense(expenses: List[Expense]):
    for expense in expenses:
        db_helper.insert_expense(expense_date=expense.expense_date, amount=expense.amount, category=expense.category,
                                 notes=expense.notes)

    return {"message": "Expenses updated successfully"}

@app.post("/analytics/expenses/monthly")
def fetch_monthly_expenses(request: MonthlyExpenseCategoryRequest):
    try:
        # Call the db_helper function with year and category parameters
        expenses = db_helper.fetch_monthly_expenses(request.year, request.category)

        if not expenses:
            raise HTTPException(
                status_code=404,
                detail="No monthly expenses found for the specified year and category"
            )

        # Construct response as a list of tuples (month_name, total_amount)
        response_expenses = []
        for expense in expenses:
            response_expenses.append({
                "month": expense[0],  # Month name
                "total_amount": expense[1]  # Total amount for the month
            })

        return response_expenses

    except ValueError as e:
        # Handle invalid category errors raised by db_helper function
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail="Failed to retrieve monthly expenses")

@app.post("/expenses/note")
def fetch_expenses_by_note(request: NoteRequest):
    expenses = db_helper.fetch_expenses_for_particular_note(request.wildcard_note, request.year, request.months)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses by the specified note from the database")

    response_expenses = []
    for expense in expenses:
        response_expenses.append({
            "expense_date": expense['expense_date'],
            "amount": expense['amount'],
            "category": expense['category'],
            "notes": expense['notes']
        })

    return response_expenses

@app.post("/analytics/getexpensesbydaterange/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary for the provided date range from the database")

    grand_total = 0
    for row in data:
        grand_total += row['Total']

    breakdown={}
    for row in data:
        percentage = (row['Total']/grand_total)*100 if grand_total != 0 else 0

        breakdown[row['category']] = {
            "Total": row["Total"],
            "Percentage": percentage
        }

    return breakdown

@app.delete("/expenses/{expense_date}")
def delete_expenses(expense_date: date):
    db_helper.delete_expenses_for_date(expense_date)
    return {"message": "Expenses deleted successfully"}

@app.post("/expenses/category/date", response_model=List[Expense])
def fetch_expenses_by_category_and_date(request: CategoryDateRequest):
    try:
        # Call the db_helper function with the request parameters
        expenses = db_helper.fetch_expenses_for_particular_category_date(
            category=request.category,
            expense_date=request.expense_date
        )

        # Initialize an empty list to hold Expense objects
        response_expenses = []

        # Loop through each expense and append to response_expenses
        for expense in expenses:
            response_expenses.append(Expense(
                expense_date=expense['expense_date'],
                amount=expense['amount'],
                category=expense['category'],
                notes=expense['notes']
            ))

        # Return the list of Expense objects
        return response_expenses
    except ValueError as e:
        # Handle invalid category errors raised by db_helper function
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/expenses/category/period", response_model=List[Expense])
def fetch_expenses_by_category_and_period(request: CategoryPeriodRequest):
    try:
        # Call the db_helper function with the request parameters
        expenses = db_helper.fetch_expenses_by_category_and_day(
            category=request.category,
            period_of_week=request.period_of_week
        )

        # Initialize an empty list to hold Expense objects
        response_expenses = []

        # Loop through each expense and append to response_expenses
        for expense in expenses:
            response_expenses.append(Expense(
                expense_date=expense['expense_date'],
                amount=expense['amount'],
                category=expense['category'],
                notes=expense['notes']
            ))

        # Return the list of Expense objects
        return response_expenses
    except ValueError as e:
        # Handle invalid category or period errors raised by db_helper function
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/expenses/update")
def handle_updates(request: UpdateRequest):
    try:
        # Process deletions
        for update in request.updates:
            if update.new_amount == 0:  # Marked for deletion
                db_helper.delete_expense(
                    expense_date=update.old_expense_date,
                    category=update.old_category,
                    notes=update.old_notes
                )
            else:  # Process modifications
                db_helper.update_expense(
                    old_data={
                        "expense_date": update.old_expense_date,
                        "amount": update.old_amount,
                        "category": update.old_category,
                        "notes": update.old_notes
                    },
                    new_data={
                        "expense_date": update.new_expense_date,
                        "amount": update.new_amount,
                        "category": update.new_category,
                        "notes": update.new_notes
                    }
                )

        # Process additions
        for addition in request.additions:
            db_helper.add_expense(
                addition.expense_date,
                addition.amount,
                addition.category,
                addition.notes,
                check_duplicate=True
            )

        return {"message": "Operation completed successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

