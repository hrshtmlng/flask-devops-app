from flask import Flask, request, jsonify
import mysql.connector
import os, time
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# Database connection
for i in range(10):
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        print("Connected to DB")
        break
    except:
        print("Waiting for DB...")
        time.sleep(5)

cursor = db.cursor(dictionary=True)

@app.route("/")
def home():
    return jsonify({"message": "Flask DevOps App running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    hashed_password = generate_password_hash(password)

    sql = """
    INSERT INTO users (name, email, password)
    VALUES (%s, %s, %s)
    """

    values = (name, email, hashed_password)

    cursor.execute(sql, values)
    db.commit()

    return jsonify({
        "message": "User stored in database"
    }), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    sql = "SELECT * FROM users WHERE email = %s"
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password"], password):
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200

    return jsonify({
        "message": "Invalid credentials"
    }), 401

@app.route("/users")
def users():
    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()
    return jsonify(users)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)