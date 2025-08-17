# webapp.py
from flask import Flask, request, jsonify, send_from_directory, make_response
import database
import os

app = Flask(__name__, static_folder='static')

# Простой CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return make_response('', 200)

# ЕДИНСТВЕННЫЙ маршрут для действий
@app.route('/api/user/actions', methods=['POST'])
def user_actions():
    print("🔹 POST /api/user/actions — запрос получен")
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    actions = database.get_user_actions(user_id)
    return jsonify(actions)

# --- Остальные маршруты ---
@app.route('/api/stats', methods=['GET'])
def stats():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    users = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM actions")
    actions = cursor.fetchone()['count']
    conn.close()
    return jsonify({"users": users, "actions": actions})

@app.route('/api/user/profile', methods=['POST'])
def user_profile():
    user_id = request.json.get('user_id')
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















