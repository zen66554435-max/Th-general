from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "training-lab-secret-change-me")

# استخدم متغير البيئة أو مجلد مؤقت
DB_PATH = os.environ.get("DB_PATH", "/tmp/lab.db")

def get_db():
    """الاتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """تهيئة قاعدة البيانات"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # إنشاء الجداول
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL
            )
        ''')
        
        # أضف البيانات الافتراضية
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         ("student", hashlib.sha256(b"student123").hexdigest(), "student"))
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         ("admin", hashlib.sha256(b"admin123").hexdigest(), "admin"))
            
            cursor.execute("INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
                         ("Red Laptop", "Training device", 899))
            cursor.execute("INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
                         ("Blue Phone", "Demo smartphone", 499))
            cursor.execute("INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
                         ("Cloud Box", "Storage service", 79))
            
            cursor.execute("INSERT INTO flags (code) VALUES (?)", ("FLAG{idor_profile_2026}",))
            cursor.execute("INSERT INTO flags (code) VALUES (?)", ("FLAG{xss_search_2026}",))
            cursor.execute("INSERT INTO flags (code) VALUES (?)", ("FLAG{admin_api_2026}",))
            
            conn.commit()
            print("[✓] Database initialized successfully")
        except sqlite3.IntegrityError:
            print("[✓] Database already populated")
        
        conn.close()
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False
    return True

# تهيئة قاعدة البيانات عند البدء
init_db()

# ============== ROUTES ==============

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
                (username, hashlib.sha256(password.encode()).hexdigest())
            )
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session["uid"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                return redirect(url_for("dashboard"))
            else:
                msg = "Invalid username or password"
        except Exception as e:
            msg = f"Login error: {str(e)}"
    
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
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            abort(404)
        
        return render_template("profile.html", user=user)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/search")
def search():
    q = request.args.get("q", "")
    products = []
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?",
            (f"%{q}%", f"%{q}%")
        )
        products = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Search error: {e}")
    
    return render_template("search.html", q=q, products=products)

@app.route("/api/admin")
def api_admin():
    if session.get("role") != "admin":
        return jsonify({"error": "admin role required"}), 403
    
    return jsonify({
        "flag": "FLAG{admin_api_2026}",
        "message": "Training-only admin API"
    }), 200

@app.route("/challenges")
def challenges():
    return render_template("challenges.html")

@app.route("/health")
def health():
    return "ok", 200

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def server_error(error):
    return "Internal server error", 500

# ============== MAIN ==============

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
