import sqlite3
import hashlib
import os

DB_FILE = "inventory.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class Database:
    def __init__(self):
        self.setup()

    def connect(self):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    def setup(self):
        """Create all tables and default admin user."""
        conn = self.connect()
        c = conn.cursor()

        # Products table
        c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                category    TEXT DEFAULT 'General',
                price       REAL DEFAULT 0,
                quantity    INTEGER DEFAULT 0,
                status      TEXT DEFAULT 'In Stock',
                description TEXT DEFAULT '',
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role     TEXT DEFAULT 'staff'
            )
        """)

        # Stock history table
        c.execute("""
            CREATE TABLE IF NOT EXISTS stock_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                change     INTEGER,
                reason     TEXT,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Default admin user
        c.execute("SELECT * FROM users WHERE username = 'admin'")
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", hash_password("admin123"), "admin")
            )

        # Sample products
        c.execute("SELECT COUNT(*) FROM products")
        if c.fetchone()[0] == 0:
            samples = [
                ("Running Shoes",    "Footwear",     1299.00, 25,  "Premium running shoes"),
                ("Cotton T-Shirt",   "Clothing",      499.00,  3,  "100% cotton, all sizes"),
                ("Water Bottle",     "Accessories",   299.00,  0,  "1 litre stainless steel"),
                ("Laptop Bag",       "Accessories",  1899.00, 10,  "15 inch laptop bag"),
                ("Wireless Mouse",   "Electronics",   799.00,  4,  "USB wireless mouse"),
                ("Notebook Pack",    "Stationery",    149.00, 50,  "Pack of 3 notebooks"),
                ("Phone Stand",      "Accessories",   349.00,  2,  "Adjustable phone stand"),
                ("Desk Lamp",        "Electronics",  1299.00,  8,  "LED desk lamp with USB"),
            ]
            for s in samples:
                qty = s[3]
                status = self._calc_status(qty)
                c.execute(
                    "INSERT INTO products (name, category, price, quantity, status, description) VALUES (?,?,?,?,?,?)",
                    (s[0], s[1], s[2], qty, status, s[4])
                )

        conn.commit()
        conn.close()

    # ─── STATUS HELPER ───────────────────────────────────────

    def _calc_status(self, qty):
        if qty == 0:
            return "Out of Stock"
        elif qty <= 5:
            return "Low Stock"
        return "In Stock"

    # ─── PRODUCTS ────────────────────────────────────────────

    def get_products(self, search="", category="", status=""):
        conn = self.connect()
        query = "SELECT id, name, category, price, quantity, status, description FROM products WHERE 1=1"
        params = []
        if search:
            query += " AND (name LIKE ? OR category LIKE ? OR description LIKE ?)"
            params += [f"%{search}%", f"%{search}%", f"%{search}%"]
        if category:
            query += " AND category = ?"
            params.append(category)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY name ASC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [tuple(r) for r in rows]

    def get_product_by_id(self, pid):
        conn = self.connect()
        row = conn.execute(
            "SELECT id, name, category, price, quantity, status, description FROM products WHERE id=?", (pid,)
        ).fetchone()
        conn.close()
        return tuple(row) if row else None

    def add_product(self, name, category, price, quantity, description=""):
        status = self._calc_status(quantity)
        conn = self.connect()
        conn.execute(
            "INSERT INTO products (name, category, price, quantity, status, description) VALUES (?,?,?,?,?,?)",
            (name, category, price, quantity, status, description)
        )
        conn.commit()
        conn.close()

    def update_product(self, pid, name, category, price, quantity, description=""):
        status = self._calc_status(quantity)
        conn = self.connect()
        conn.execute(
            """UPDATE products SET name=?, category=?, price=?, quantity=?,
               status=?, description=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
            (name, category, price, quantity, status, description, pid)
        )
        conn.commit()
        conn.close()

    def delete_product(self, pid):
        conn = self.connect()
        conn.execute("DELETE FROM products WHERE id=?", (pid,))
        conn.commit()
        conn.close()

    def restock_product(self, pid, qty):
        conn = self.connect()
        conn.execute("UPDATE products SET quantity = quantity + ?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (qty, pid))
        # Get updated quantity for status
        row = conn.execute("SELECT quantity FROM products WHERE id=?", (pid,)).fetchone()
        if row:
            new_status = self._calc_status(row[0])
            conn.execute("UPDATE products SET status=? WHERE id=?", (new_status, pid))
        # Log history
        conn.execute(
            "INSERT INTO stock_history (product_id, change, reason) VALUES (?,?,?)",
            (pid, qty, "Manual restock")
        )
        conn.commit()
        conn.close()

    def get_categories(self):
        conn = self.connect()
        rows = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_low_stock(self):
        conn = self.connect()
        rows = conn.execute(
            "SELECT id, name, category, quantity, status FROM products WHERE status IN ('Low Stock','Out of Stock') ORDER BY quantity ASC"
        ).fetchall()
        conn.close()
        return [tuple(r) for r in rows]

    def get_recent_products(self, limit=5):
        conn = self.connect()
        rows = conn.execute(
            "SELECT id, name, category, price, quantity, status FROM products ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [tuple(r) for r in rows]

    # ─── STATS ───────────────────────────────────────────────

    def get_stats(self):
        conn = self.connect()
        c = conn.cursor()
        total     = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        in_stock  = c.execute("SELECT COUNT(*) FROM products WHERE status='In Stock'").fetchone()[0]
        low       = c.execute("SELECT COUNT(*) FROM products WHERE status='Low Stock'").fetchone()[0]
        out       = c.execute("SELECT COUNT(*) FROM products WHERE status='Out of Stock'").fetchone()[0]
        value     = c.execute("SELECT SUM(price * quantity) FROM products").fetchone()[0] or 0
        conn.close()
        return {
            "total": total,
            "in_stock": in_stock,
            "low_stock": low,
            "out_of_stock": out,
            "total_value": round(value, 2)
        }

    # ─── USERS ───────────────────────────────────────────────

    def verify_user(self, username, password):
        conn = self.connect()
        row = conn.execute(
            "SELECT id, username, password, role FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        return tuple(row) if row else None

    def get_all_users(self):
        conn = self.connect()
        rows = conn.execute("SELECT id, username, role FROM users ORDER BY role").fetchall()
        conn.close()
        return [tuple(r) for r in rows]

    def add_user(self, username, password, role="staff"):
        conn = self.connect()
        try:
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                (username, hash_password(password), role)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Username already exists
        conn.close()
