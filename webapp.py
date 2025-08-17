# webapp.py
from flask import Flask, request, jsonify, send_from_directory
import database
import os

app = Flask(__name__, static_folder='static')

# Простой CORS
@app.after_request
def after_request(response):
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
    return response

# --- API: статистика ---
@app.route('/api/stats', methods=['GET'])
def stats():
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM actions")
        actions = cursor.fetchone()['count']
        conn.close()
        return jsonify({"users": users, "actions": actions})
    except Exception as e:
        return jsonify({"error": "server error"}), 500

# --- API: профиль ---
@app.route('/api/user/profile', methods=['GET'])
def user_profile():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, first_name, last_name, created_at 
            FROM users WHERE id = %s
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify({
                "username": row["username"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "created_at": row["created_at"].isoformat()
            })
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": "server error"}), 500

# --- API: действия ---
@app.route('/api/user/actions', methods=['GET'])
def user_actions():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    try:
        actions = database.get_user_actions(int(user_id))
        return jsonify(actions)
    except Exception as e:
        return jsonify({"error": "server error"}), 500

# --- API: сохранить сообщение ---
@app.route('/api/user/message', methods=['POST'])
def save_message():
    user_id = request.json.get('user_id')
    text = request.json.get('text')
    if not user_id or not text:
        return jsonify({"error": "user_id or text missing"}), 400
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (user_id, message_text, timestamp)
            VALUES (%s, %s, NOW())
        """, (user_id, text))
        conn.commit()
        conn.close()
        return jsonify({"status": "saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- API: получить сообщения ---
@app.route('/api/user/messages', methods=['GET'])
def get_messages():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT message_text, timestamp FROM messages
            WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        messages = [{"text": row["message_text"], "time": row["timestamp"]} for row in rows]
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# --- Статика ---
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# --- Запуск ---
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    database.init_db()
    app.run(host="0.0.0.0", port=port)

















