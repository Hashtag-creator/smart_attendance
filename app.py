from flask import Flask, request, jsonify, render_template
import pyodbc
import os
from dotenv import load_dotenv
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable Cross-Origin requests if needed
load_dotenv()

def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=jebastin.database.windows.net;'
            'DATABASE=attendance_system;'
            'UID=jebastin;'
            'PWD=Antic@123'
        )
        print("✅ Connected to database")
        return conn
    except Exception as e:
        print("❌ Database connection error:", e)
        raise



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.get_json()
        username = data.get("username", "").strip()

        if not username:
            return jsonify({'status': 'Username cannot be empty'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            cursor.execute("INSERT INTO Attendance (user_id) VALUES (?)", (user[0],))
            conn.commit()
            return jsonify({'status': 'Attendance marked'})
        else:
            return jsonify({'status': 'User not found'}), 404
    except Exception as e:
        print("Error in /mark-attendance:", e)
        return jsonify({'status': 'Error occurred'}), 500


@app.route('/attendance-records', methods=['GET'])
def get_records():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT U.username, A.timestamp FROM Attendance A JOIN Users U ON A.user_id = U.id ORDER BY A.timestamp DESC")
        records = [{'username': row[0], 'timestamp': row[1].isoformat()} for row in cursor.fetchall()]
        return jsonify(records)
    except Exception as e:
        print("Error in /attendance-records:", e)
        return jsonify({'error': 'Failed to retrieve data'}), 500


if __name__ == '__main__':
    app.run(debug=True)
