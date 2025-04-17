# Code to insert random data into the database

import random
from datetime import date
import db_helper

if __name__ == "__main__":
    categories = [
        "Food", "Utilities", "Housing", "Transportation",
        "Insurance", "Medical", "Debt Payment", "Entertainment",
        "Misc", "Shopping"
    ]

    # Months: January to July and October to December
    months = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
    year = 2024



    # Month names for more descriptive notes
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 10: "October",
        11: "November", 12: "December"
    }

    # Category-specific notes and amount ranges
    category_data = {
        "Food": {
            "base_amount": 100,
            "variance": 80,
            "notes": [
                "Grocery shopping", "Restaurant dinner", "Office lunch",
                "Pizza delivery", "Jatre feast", "Coffee and pastries",
                "Weekend IPL party supplies", "Meal prep ingredients", "Festival feast"
            ]
        },
        "Utilities": {
            "base_amount": 250,
            "variance": 40,
            "notes": [
                "Electricity bill", "Water bill", "Broadband service",
                "Gas bill", "Combined utilities", "Jio Postpaid"
            ]
        },
        "Housing": {
            "base_amount": 800,
            "variance": 150,
            "notes": [
                "Monthly rent", "Apartment maintenance", "Property tax installment",
                "Home insurance", "Home improvement", "Mortgage payment"
            ]
        },
        "Transportation": {
            "base_amount": 50,
            "variance": 40,
            "notes": [
                "Gas refill", "Bus pass", "Car maintenance",
                "Parking fees", "Uber rides", "Metro tickets",
                "Toll charges", "Bike repair"
            ]
        },
        "Insurance": {
            "base_amount": 1800,
            "variance": 70,
            "notes": [
                "Health insurance premium", "Car insurance", "Life insurance",
                "Renter's insurance", "Travel insurance", "Pet insurance"
            ]
        },
        "Medical": {
            "base_amount": 480,
            "variance": 80,
            "notes": [
                "Pharmacy purchase", "Doctor visit", "Prescription drugs",
                "Eye exam", "Dental cleaning", "ear wax removal",
                "Vitamins and supplements"
            ]
        },
        "Debt Payment": {
            "base_amount": 280,
            "variance": 100,
            "notes": [
                "Loan repayment", "Credit card minimum", "Gold loan payment",
                "Car loan installment", "Personal loan payment"
            ]
        },
        "Entertainment": {
            "base_amount": 365,
            "variance": 45,
            "notes": [
                "Movie tickets", "Concert tickets", "Netflix subscription",
                "Book purchase", "Gaming mouse", "IPL ticket",
                "Museum entry", "Music festival", "Video game"
            ]
        },
        "Misc": {
            "base_amount": 25,
            "variance": 35,
            "notes": [
                "Stationery", "Office supplies", "Charity donation",
                "Gift purchase", "Postage stamps", "Library Membership renewal",
                "Car wash", "Haircut", "Cleaning supplies"
            ]
        },
        "Shopping": {
            "base_amount": 1200,
            "variance": 100,
            "notes": [
                "Clothes shopping", "iMac purchase", "Home decor",
                "Kitchen gadgets", "Furniture", "Tennis racquet",
                "Seasonal items", "Hair gel", "Asics Shoes"
            ]
        }
    }

    # Seasonal adjustments to make amounts more realistic
    seasonal_multipliers = {
        1: {"Food": 1.1, "Entertainment": 0.7, "Utilities": 1.3},
        2: {"Shopping": 0.8, "Food": 0.9, "Utilities": 1.2},
        3: {"Shopping": 1.1, "Food": 1.0, "Utilities": 1.1},
        4: {"Food": 1.0, "Shopping": 1.1, "Utilities": 0.9},
        5: {"Food": 1.1, "Entertainment": 1.2, "Shopping": 1.2},
        6: {"Entertainment": 1.3, "Food": 1.2, "Utilities": 0.9},
        7: {"Entertainment": 1.4, "Food": 1.3, "Utilities": 1.0},
        10: {"Shopping": 1.2, "Food": 1.1, "Utilities": 1.0},
        11: {"Shopping": 1.4, "Food": 1.2, "Utilities": 1.1},
        12: {"Shopping": 1.6, "Food": 1.3, "Entertainment": 1.3}
    }

    # Insert data with variety and float whole numbers only
    for month in months:
        for category in categories:
            base = category_data[category]["base_amount"]
            variance = category_data[category]["variance"]
            multiplier = seasonal_multipliers.get(month, {}).get(category, 1.0)
            min_amount = int((base - (variance * 0.3)) * multiplier)
            max_amount = int((base + variance) * multiplier)
            amount_int = random.randint(max(min_amount, 1), max_amount)
            amount = float(amount_int)  # Ensure float type, but whole number (e.g., 120.0)

            note = random.choice(category_data[category]["notes"])
            if random.random() < 0.3:
                note = f"{month_names[month]} {note}"
            day = random.randint(1, 28)
            expense_date = date(year, month, day).isoformat()

            try:
                db_helper.insert_expense(expense_date, amount, category, note)
                print(f"Inserted: {expense_date}, ${amount:.2f}, {category}, {note}")
            except Exception as e:
                print(f"Failed to insert {category} for {expense_date}: {e}")
