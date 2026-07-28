"""
Expense Tracker - Flask Application
A production-ready personal finance tracking web application.

This module contains the application factory, database access layer,
validation logic, and all HTTP routes for the Expense Tracker.
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "expense.db")

VALID_CATEGORIES = (
    "Food",
    "Shopping",
    "Education",
    "Travel",
    "Transport",
    "Entertainment",
    "Healthcare",
    "Bills",
    "Other",
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "expense-tracker-secret-key-change-in-production"


# --------------------------------------------------------------------------
# Database Layer
# --------------------------------------------------------------------------

def get_db_connection():
    """Create and return a new SQLite database connection.

    The connection uses a row factory so query results behave like
    dictionaries, which keeps template rendering and JSON conversion simple.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """Initialize the SQLite database and create the expenses table.

    This function is idempotent and safe to call on every application
    startup; it only creates the table if it does not already exist.
    """
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            description TEXT,
            transaction_type TEXT NOT NULL DEFAULT 'expense',
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


# --------------------------------------------------------------------------
# Validation Layer
# --------------------------------------------------------------------------

def validate_expense_form(form_data):
    """Validate expense form data and return (errors, cleaned_data).

    Args:
        form_data: A mapping-like object (e.g. request.form) containing
            the submitted expense fields.

    Returns:
        A tuple of (errors, cleaned_data) where errors is a dict mapping
        field names to human-readable error messages, and cleaned_data is
        a dict of sanitized values ready for persistence.
    """
    errors = {}

    title = (form_data.get("title") or "").strip()
    amount_raw = (form_data.get("amount") or "").strip()
    category = (form_data.get("category") or "").strip()
    expense_date = (form_data.get("expense_date") or "").strip()
    description = (form_data.get("description") or "").strip()
    transaction_type = (form_data.get("transaction_type") or "expense").strip()

    if not title:
        errors["title"] = "Title is required."
    elif len(title) > 100:
        errors["title"] = "Title must be under 100 characters."

    amount_value = None
    if not amount_raw:
        errors["amount"] = "Amount is required."
    else:
        try:
            amount_value = float(amount_raw)
            if amount_value <= 0:
                errors["amount"] = "Amount must be greater than zero."
        except ValueError:
            errors["amount"] = "Amount must be a valid number."

    if not category:
        errors["category"] = "Category is required."
    elif category not in VALID_CATEGORIES:
        errors["category"] = "Please select a valid category."

    if not expense_date:
        errors["expense_date"] = "Date is required."
    else:
        try:
            parsed_date = datetime.strptime(expense_date, "%Y-%m-%d")
            if parsed_date.date() > datetime.now().date():
                errors["expense_date"] = "Date cannot be in the future."
        except ValueError:
            errors["expense_date"] = "Please enter a valid date."

    if len(description) > 500:
        errors["description"] = "Description must be under 500 characters."

    if transaction_type not in ("expense", "income"):
        transaction_type = "expense"

    cleaned_data = {
        "title": title,
        "amount": amount_value,
        "category": category,
        "expense_date": expense_date,
        "description": description,
        "transaction_type": transaction_type,
    }

    return errors, cleaned_data


# --------------------------------------------------------------------------
# Data Access Helpers
# --------------------------------------------------------------------------

def fetch_all_expenses(search_term="", category_filter="", type_filter=""):
    """Fetch expenses from the database with optional search and filters.

    Args:
        search_term: Free-text term matched against title and description.
        category_filter: Restrict results to a single category if provided.
        type_filter: Restrict results to 'income' or 'expense' if provided.

    Returns:
        A list of sqlite3.Row objects ordered by most recent date first.
    """
    connection = get_db_connection()
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if search_term:
        query += " AND (title LIKE ? OR description LIKE ?)"
        like_term = f"%{search_term}%"
        params.extend([like_term, like_term])

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    if type_filter:
        query += " AND transaction_type = ?"
        params.append(type_filter)

    query += " ORDER BY expense_date DESC, id DESC"

    rows = connection.execute(query, params).fetchall()
    connection.close()
    return rows


def calculate_summary(expenses):
    """Calculate dashboard summary statistics from a list of expense rows."""
    total_income = sum(row["amount"] for row in expenses if row["transaction_type"] == "income")
    total_expenses = sum(row["amount"] for row in expenses if row["transaction_type"] == "expense")

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "remaining_balance": round(total_income - total_expenses, 2),
        "total_transactions": len(expenses),
    }


def get_expense_or_none(expense_id):
    """Fetch a single expense by id, returning None if it does not exist."""
    connection = get_db_connection()
    row = connection.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    connection.close()
    return row


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.route("/")
def dashboard():
    """Render the main dashboard with summary stats and recent expenses."""
    search_term = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "").strip()
    type_filter = request.args.get("type", "").strip()

    all_expenses = fetch_all_expenses()
    summary = calculate_summary(all_expenses)

    filtered_expenses = fetch_all_expenses(search_term, category_filter, type_filter)

    return render_template(
        "index.html",
        summary=summary,
        expenses=filtered_expenses,
        categories=VALID_CATEGORIES,
        search_term=search_term,
        category_filter=category_filter,
        type_filter=type_filter,
    )


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    """Render the add-expense form and handle its submission."""
    if request.method == "POST":
        errors, cleaned_data = validate_expense_form(request.form)

        if errors:
            return render_template(
                "add_expense.html",
                categories=VALID_CATEGORIES,
                errors=errors,
                form_data=cleaned_data,
            )

        connection = get_db_connection()
        connection.execute(
            """
            INSERT INTO expenses
                (title, amount, category, expense_date, description, transaction_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cleaned_data["title"],
                cleaned_data["amount"],
                cleaned_data["category"],
                cleaned_data["expense_date"],
                cleaned_data["description"],
                cleaned_data["transaction_type"],
                datetime.now().isoformat(),
            ),
        )
        connection.commit()
        connection.close()

        flash("Transaction added successfully.", "success")
        return redirect(url_for("dashboard"))

    default_data = {
        "title": "",
        "amount": "",
        "category": "",
        "expense_date": datetime.now().strftime("%Y-%m-%d"),
        "description": "",
        "transaction_type": "expense",
    }
    return render_template(
        "add_expense.html",
        categories=VALID_CATEGORIES,
        errors={},
        form_data=default_data,
    )


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    """Render the edit-expense form and handle its submission."""
    existing_expense = get_expense_or_none(expense_id)
    if existing_expense is None:
        flash("The requested transaction could not be found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        errors, cleaned_data = validate_expense_form(request.form)

        if errors:
            return render_template(
                "edit_expense.html",
                categories=VALID_CATEGORIES,
                errors=errors,
                form_data=cleaned_data,
                expense_id=expense_id,
            )

        connection = get_db_connection()
        connection.execute(
            """
            UPDATE expenses
            SET title = ?, amount = ?, category = ?, expense_date = ?,
                description = ?, transaction_type = ?
            WHERE id = ?
            """,
            (
                cleaned_data["title"],
                cleaned_data["amount"],
                cleaned_data["category"],
                cleaned_data["expense_date"],
                cleaned_data["description"],
                cleaned_data["transaction_type"],
                expense_id,
            ),
        )
        connection.commit()
        connection.close()

        flash("Transaction updated successfully.", "success")
        return redirect(url_for("dashboard"))

    form_data = {
        "title": existing_expense["title"],
        "amount": existing_expense["amount"],
        "category": existing_expense["category"],
        "expense_date": existing_expense["expense_date"],
        "description": existing_expense["description"] or "",
        "transaction_type": existing_expense["transaction_type"],
    }
    return render_template(
        "edit_expense.html",
        categories=VALID_CATEGORIES,
        errors={},
        form_data=form_data,
        expense_id=expense_id,
    )


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    """Delete a single expense by id and redirect back to the dashboard."""
    existing_expense = get_expense_or_none(expense_id)
    if existing_expense is None:
        flash("The requested transaction could not be found.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    connection.commit()
    connection.close()

    flash("Transaction deleted successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def api_get_expense(expense_id):
    """Return a single expense as JSON, used for client-side confirmations."""
    existing_expense = get_expense_or_none(expense_id)
    if existing_expense is None:
        return jsonify({"error": "Transaction not found."}), 404

    return jsonify(
        {
            "id": existing_expense["id"],
            "title": existing_expense["title"],
            "amount": existing_expense["amount"],
            "category": existing_expense["category"],
            "expense_date": existing_expense["expense_date"],
            "description": existing_expense["description"],
            "transaction_type": existing_expense["transaction_type"],
        }
    )


@app.errorhandler(404)
def handle_not_found(_error):
    """Redirect unknown routes back to the dashboard."""
    flash("The page you requested does not exist.", "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()