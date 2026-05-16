from flask import Flask, request, jsonify, render_template
import mysql.connector
import time
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# ---------------- DB INIT ----------------
db = None
cursor = None

# Retry DB connection
for i in range(10):
    try:
        db = mysql.connector.connect(
            host="db",
            user="flaskuser",
            password="flaskpass123",
            database="flask_app"
        )
        cursor = db.cursor(dictionary=True)
        print("DB connected")
        break
    except Exception as e:
        print("DB not available:", e)
        time.sleep(2)

# If DB still not connected → exit (prevents crash loops)
if db is None or cursor is None:
    print("Failed to connect to DB after retries. Exiting...")
    exit(1)

# Create table safely
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password TEXT
    )
    """)
    db.commit()
except Exception as e:
    print("Error creating table:", e)

# ---------------- ROUTES ----------------

# UI route
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/register", methods=["POST"])
def register():
    if cursor is None:
        return {"error": "database not connected"}, 500

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        db.commit()
        return {"message": "User stored in database"}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@app.route("/login", methods=["POST"])
def login():
    if cursor is None:
        return {"error": "database not connected"}, 500

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password"], password):
        return {
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }, 200

    return {"message": "Invalid credentials"}, 401


@app.route("/users")
def users():
    if cursor is None:
        return {"error": "database not connected"}, 500

    cursor.execute("SELECT id, name, email FROM users")
    return jsonify(cursor.fetchall())


# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)