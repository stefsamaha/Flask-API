#!/usr/bin/python

from flask import Flask, request, jsonify
from flask_cors import CORS  # Optional for handling cross-origin requests
import sqlite3

def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        ''')
        conn.commit()
        print("User table created successfully or already exists.")
    except Exception as e:
        print(f"User table creation failed - {e}")  # This will print the exact error message
    finally:
        conn.close()

if __name__ == "__main__":
    create_db_table()

def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)", 
                    (user['name'], user['email'], user['phone'], user['address'], user['country']) )
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()
    return inserted_user

def get_users(): 
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        # convert row objects to dictionary
        for i in rows:
            user = {}
            user["user_id"] = i["user_id"]
            user["name"] = i["name"]
            user["email"] = i["email"]
            user["phone"] = i["phone"]
            user["address"] = i["address"]
            user["country"] = i["country"]
            users.append(user)
    except Exception as e:
        print(f"Error occurred: {e}")
        users = []
    finally:
        conn.close()
    return users

def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            user["user_id"] = row["user_id"]
            user["name"] = row["name"]
            user["email"] = row["email"]
            user["phone"] = row["phone"]
            user["address"] = row["address"]
            user["country"] = row["country"]
        else:
            user = {"error": "User not found"}
    except Exception as e:
        print(f"Error occurred: {e}")
        user = {"error": "An error occurred while retrieving the user."}
    finally:
        conn.close()
    return user

def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id=?", 
                    (user["name"], user["email"], user["phone"], user["address"], user["country"], user["user_id"]))
        conn.commit()
        updated_user = get_user_by_id(user["user_id"])
    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()
    return updated_user

def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE from users WHERE user_id = ?", (user_id,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()
        message["status"] = "Cannot delete user"
    finally:
        conn.close()
    return message


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Root route to handle requests to "/"
@app.route('/')
def home():
    return "Welcome to the Flask API!"

@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users())

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))

@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    try:
        user = request.get_json()
        if not all(key in user for key in ("name", "email", "phone", "address", "country")):
            return jsonify({"error": "Missing required fields"}), 400
        return jsonify(insert_user(user))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/update', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))

@app.route('/api/users/delete/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))

if __name__ == "__main__":
    app.run(debug=True)
