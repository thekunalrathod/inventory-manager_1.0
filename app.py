from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from database import Database
from reports import export_excel, export_pdf
import io

app = Flask(__name__)
app.secret_key = "inventory_secret_key_2024"
db = Database()

# ─────────────────────────────────────────
#  AUTH MIDDLEWARE
# ─────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = db.verify_user(username, password)
        if user:
            session["user"] = {"id": user[0], "username": user[1], "role": user[3]}
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    stats = db.get_stats()
    low_stock = db.get_low_stock()
    recent = db.get_recent_products(5)
    return render_template("dashboard.html",
                           stats=stats,
                           low_stock=low_stock,
                           recent=recent,
                           user=session["user"])


# ─────────────────────────────────────────
#  PRODUCTS
# ─────────────────────────────────────────

@app.route("/products")
@login_required
def products():
    search = request.args.get("search", "")
    category = request.args.get("category", "")
    status = request.args.get("status", "")
    all_products = db.get_products(search=search, category=category, status=status)
    categories = db.get_categories()
    return render_template("products.html",
                           products=all_products,
                           categories=categories,
                           search=search,
                           selected_category=category,
                           selected_status=status,
                           user=session["user"])


@app.route("/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        category = request.form.get("category", "General").strip()
        price    = float(request.form.get("price", 0))
        quantity = int(request.form.get("quantity", 0))
        description = request.form.get("description", "").strip()

        if not name:
            return render_template("product_form.html",
                                   error="Product name is required.",
                                   user=session["user"], action="Add")

        db.add_product(name, category, price, quantity, description)
        return redirect(url_for("products"))

    return render_template("product_form.html",
                           user=session["user"], action="Add", product=None)


@app.route("/products/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def edit_product(pid):
    product = db.get_product_by_id(pid)
    if not product:
        return redirect(url_for("products"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        category = request.form.get("category", "General").strip()
        price    = float(request.form.get("price", 0))
        quantity = int(request.form.get("quantity", 0))
        description = request.form.get("description", "").strip()
        db.update_product(pid, name, category, price, quantity, description)
        return redirect(url_for("products"))

    return render_template("product_form.html",
                           user=session["user"], action="Edit", product=product)


@app.route("/products/delete/<int:pid>", methods=["POST"])
@login_required
def delete_product(pid):
    if session["user"]["role"] != "admin":
        return jsonify({"error": "Only admin can delete products"}), 403
    db.delete_product(pid)
    return redirect(url_for("products"))


@app.route("/products/restock/<int:pid>", methods=["POST"])
@login_required
def restock(pid):
    qty = int(request.form.get("qty", 0))
    db.restock_product(pid, qty)
    return redirect(url_for("products"))


# ─────────────────────────────────────────
#  API ENDPOINTS (JSON)
# ─────────────────────────────────────────

@app.route("/api/products", methods=["GET"])
@login_required
def api_products():
    products = db.get_products()
    result = []
    for p in products:
        result.append({
            "id": p[0], "name": p[1], "category": p[2],
            "price": p[3], "quantity": p[4],
            "status": p[5], "description": p[6]
        })
    return jsonify(result)


@app.route("/api/stats", methods=["GET"])
@login_required
def api_stats():
    return jsonify(db.get_stats())


# ─────────────────────────────────────────
#  REPORTS & EXPORT
# ─────────────────────────────────────────

@app.route("/export/excel")
@login_required
def export_to_excel():
    products = db.get_products()
    output = export_excel(products)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="inventory_report.xlsx"
    )


@app.route("/export/pdf")
@login_required
def export_to_pdf():
    products = db.get_products()
    stats = db.get_stats()
    output = export_pdf(products, stats)
    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="inventory_report.pdf"
    )


# ─────────────────────────────────────────
#  USER MANAGEMENT (Admin Only)
# ─────────────────────────────────────────

@app.route("/users")
@login_required
def users():
    if session["user"]["role"] != "admin":
        return redirect(url_for("dashboard"))
    all_users = db.get_all_users()
    return render_template("users.html", users=all_users, user=session["user"])


@app.route("/users/add", methods=["POST"])
@login_required
def add_user():
    if session["user"]["role"] != "admin":
        return redirect(url_for("dashboard"))
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role     = request.form.get("role", "staff")
    db.add_user(username, password, role)
    return redirect(url_for("users"))


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Inventory Management System")
    print("  Built by Kunal Rathod")
    print("  Open browser: http://localhost:5000")
    print("  Login: admin / admin123")
    print("="*50 + "\n")
    app.run(debug=True)
