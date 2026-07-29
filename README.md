# 💰 Expense Tracker

A clean, modern, and fully responsive personal finance tracker built with **Flask**, **SQLite**, and **vanilla JavaScript** — designed with a soft pastel, glassmorphism aesthetic that feels like a premium SaaS product.



## ✨ Overview

Expense Tracker helps you log, organize, and understand your income and spending at a glance. It combines a lightweight Python/Flask backend with a hand-crafted, dependency-free frontend to deliver a fast, elegant, and accessible experience — no frontend framework, no build step, just clean code.

This project was built as a portfolio-grade showcase of full-stack fundamentals: server-side rendering with Jinja2, relational data modeling with SQLite, RESTful route design, robust server-side validation, and a polished, hand-designed UI.

## 🚀 Features

### Dashboard
- Real-time summary cards: **Total Income**, **Total Expenses**, **Remaining Balance**, and **Total Transactions**
- A live, searchable, filterable transaction table
- Elegant empty states when no data matches

### Transaction Management
- Add income or expense transactions
- Edit existing transactions (pre-filled forms)
- Delete transactions with an animated confirmation modal
- Search by title or description
- Filter by category and by transaction type (income/expense)

### Categories
`Food` · `Shopping` · `Education` · `Travel` · `Transport` · `Entertainment` · `Healthcare` · `Bills` · `Other`

### Validation
Every form is validated on both the client and the server:
- Empty required fields are rejected
- Amounts must be positive numbers
- Dates cannot be set in the future
- Categories must match an allowed list
- Friendly, inline error messages guide the user to a fix

### Experience & Polish
- Soft pastel palette (lavender, mint, baby blue, peach, blush pink, cream) — no dark mode, no neon
- Glassmorphism cards with soft shadows and blurred surfaces
- Smooth fade-in page transitions and hover animations
- Ripple effect on buttons
- Auto-dismissing success/error toast notifications
- Animated confirmation dialog before any deletion
- Fully responsive, mobile-first layout
- Accessible focus states and semantic HTML

## 🗂️ Folder Structure

```
Expense-Tracker/
│
├── app.py                  # Flask application, routes, validation, and DB logic
├── requirements.txt        # Python dependencies
├── expense.db               # SQLite database (auto-created on first run)
├── README.md
│
├── templates/
│   ├── index.html           # Dashboard
│   ├── add_expense.html     # Add transaction form
│   └── edit_expense.html    # Edit transaction form
│
└── static/
    ├── style.css             # Design system & styling
    └── script.js             # Client-side validation, ripple, modal, toasts
```

## 🛠️ Technologies Used

| Layer      | Technology                  |
|------------|------------------------------|
| Backend    | Python, Flask                |
| Database   | SQLite (via `sqlite3`)       |
| Frontend   | HTML5, CSS3, Vanilla JavaScript |
| Fonts      | Sora, Plus Jakarta Sans (Google Fonts) |

No frontend frameworks, no build tools, no external JS libraries — just clean, dependency-light code.

## ⚙️ Installation Guide

**Prerequisites:** Python 3.9+ and `pip` installed on your machine.

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/santoshikumbhar3-art/Expense-Tracker.git
   cd Expense-Tracker
   ```

2. **(Recommended) Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   The SQLite database (`expense.db`) is created automatically on first run — no manual setup required.

5. **Open your browser**
   Visit **http://127.0.0.1:5000** to start tracking your expenses.

## 📸 Screenshots

> _Add screenshots of your running application here to showcase the UI._

| Dashboard | Add Transaction |
|-----------|------------------|
| `screenshots/dashboard.png` | `screenshots/add-transaction.png` |

## 🔭 Future Improvements

- User authentication and multi-user support
- Monthly and category-wise spending charts (bar/pie/line)
- CSV/PDF export of transaction history
- Recurring transaction support (subscriptions, salary)
- Budget goals with progress tracking and alerts
- Dark mode as an optional theme toggle
- Pagination for large transaction histories
- Deployment guide for Render/Railway/Heroku

## 📄 License

This project is open-source and available for personal and educational use.

---

Built with care for clean code, thoughtful UX, and a portfolio-ready finish.
