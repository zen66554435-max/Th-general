from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3, os, hashlib, secrets
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "training-lab-secret-change-me")

# استخدم /tmp للـ database
DB = os.path.join(tempfile.gettempdir(), "lab.db")

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    try:
        c = db()
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT);
        CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, name TEXT, description TEXT, price INTEGER);
        CREATE TABLE IF NOT EXISTS flags(id INTEGER PRIMARY KEY, code TEXT UNIQUE);
        """)
        if not c.execute("SELECT 1 FROM users WHERE username='student'").fetchone():
            c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",("student",hashlib.sha256(b"student123").hexdigest(),"student"))
            c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",("admin",hashlib.sha256(b"admin123").hexdigest(),"admin"))
            c.executemany("INSERT INTO products(name,description,price) VALUES(?,?,?)",[
                ("Red Laptop","Training device",899),("Blue Phone","Demo smartphone",499),("Cloud Box","Storage service",79)])
            c.executemany("INSERT INTO flags(code) VALUES(?)",[
                ("FLAG{idor_profile_2026}",),("FLAG{xss_search_2026}",),("FLAG{admin_api_2026}",)])
            c.commit()
        c.close()
    except Exception as e:
        print(f"[ERROR] Database initialization: {e}")

@app.route("/")
def home(): 
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    msg = ""
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        try:
            row = db().execute("SELECT * FROM users WHERE username=? AND password=?", (u, hashlib.sha256(p.encode()).hexdigest())).fetchone()
            if row:
                session["uid"] = row["id"]
                session["username"] = row["username"]
                session["role"] = row["role"]
                return redirect(url_for("dashboard"))
            msg = "Invalid credentials"
        except Exception as e:
            msg = f"Error: {str(e)}"
    return render_template("login.html", msg=msg)

@app.route("/logout")
def logout(): 
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "uid" not in session: 
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/profile/<int:user_id>")
def profile(user_id):
    try:
        row = db().execute("SELECT id,username,role FROM users WHERE id=?", (user_id,)).fetchone()
        if not row: 
            abort(404)
        return render_template("profile.html", user=row)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/search")
def search():
    try:
        q = request.args.get("q", "")
        rows = db().execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ?", (f"%{q}%", f"%{q}%")).fetchall()
        return render_template("search.html", q=q, products=rows)
    except Exception as e:
        return f"Search Error: {str(e)}", 500

@app.route("/api/admin")
def api_admin():
    if session.get("role") != "admin":
        return jsonify(error="admin role required"), 403
    return jsonify(flag="FLAG{admin_api_2026}", message="Training-only admin API")

@app.route("/challenges")
def challenges(): 
    return render_template("challenges.html")

@app.route("/health")
def health(): 
    return "ok", 200

@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error", 500

@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404

init()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
