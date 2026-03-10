# Inventory Management System — Web App

A full-stack web-based inventory management system built with **Python + Flask + SQLite**.

Built by **Kunal Rathod** | [kunalrathod.in](http://kunalrathod.in)

---

## Features

- **Login System** — Admin and Staff roles with password hashing (SHA-256)
- **Dashboard** — Live stats, inventory value, low stock alerts, recently updated
- **Products** — Full CRUD (Add, View, Edit, Delete, Restock)
- **Search & Filter** — Search by name, filter by category and stock status
- **Auto Stock Status** — In Stock / Low Stock / Out of Stock (auto-calculated)
- **Export to Excel** — Download full inventory as formatted .xlsx file
- **Export to PDF** — Download inventory report as formatted PDF
- **User Management** — Admin can add/view users (Admin panel)
- **REST API** — JSON endpoints for products and stats

---

## Tech Stack

| Layer       | Technology                     |
|-------------|-------------------------------|
| Backend     | Python 3, Flask                |
| Database    | SQLite (via Python sqlite3)    |
| Frontend    | HTML, CSS, JavaScript          |
| Auth        | Session-based + SHA-256 hashing|
| Export      | openpyxl (Excel), reportlab (PDF) |
| API         | Flask JSON endpoints           |

---

## Project Structure

```
inventory-manager/
│
├── app.py            ← Main Flask application + all routes
├── database.py       ← All database operations (SQLite)
├── reports.py        ← Excel and PDF export logic
├── requirements.txt  ← Python dependencies
│
└── templates/
    ├── base.html         ← Sidebar layout (shared)
    ├── login.html        ← Login page
    ├── dashboard.html    ← Home dashboard
    ├── products.html     ← Products list + search
    ├── product_form.html ← Add / Edit product
    └── users.html        ← User management (admin only)
```

---

## How to Run

### Step 1 — Install Python
Download from [python.org](https://python.org) — tick "Add to PATH" during install.

### Step 2 — Install Dependencies
```bash
pip install flask openpyxl reportlab
```

### Step 3 — Run the App
```bash
python app.py
```

### Step 4 — Open Browser
```
http://localhost:5000
```

### Default Login
```
Username: admin
Password: admin123
```

---

## API Endpoints

| Method | Endpoint        | Description           |
|--------|-----------------|-----------------------|
| GET    | /api/products   | Get all products JSON |
| GET    | /api/stats      | Get inventory stats   |
| GET    | /export/excel   | Download Excel report |
| GET    | /export/pdf     | Download PDF report   |

---

## Screenshots

> Dashboard with stats, alerts, and inventory value
> Products table with search, filter, and actions
> Export to Excel and PDF with one click

---

## What I Learned Building This

- Flask routing, templates, and session management
- SQLite database design and SQL queries (CRUD)
- Password hashing for secure user authentication
- Role-based access control (Admin vs Staff)
- REST API design with JSON responses
- Excel and PDF generation from Python
- Full MVC project structure

---

## Next Improvements

- [ ] PostgreSQL instead of SQLite (production ready)
- [ ] Email alerts when stock goes low
- [ ] Sales tracking and invoicing module
- [ ] Charts and graphs on dashboard
- [ ] Deploy on Railway or Render (live URL)

---

## About Me

I'm Kunal Rathod, a self-taught web developer from Gandhinagar, Gujarat.
I build websites using WordPress and Shopify and I'm learning Python for backend development.

- Email: kunalrathod9527@gmail.com
- Website: kunalrathod.in
