# webapp.py
from flask import Flask, request, jsonify, send_from_directory, make_response
import database
import os

app = Flask(__name__, static_folder='static')

# ---------------------
# МАКСИМАЛЬНО ПРОСТОЙ CORS ДЛЯ TELEGRAM
# ---------------------

@app.after_request
def after_request(response):
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/api/user/actions', methods=['POST', 'OPTIONS'])
def user_actions():
    if request.method == 'OPTIONS':
        return make_response('', 200)
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id required"}), 400
        actions = database.get_user_actions(user_id)
        return jsonify(actions)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "server error"}), 500

@app.route('/api/stats', methods=['GET', 'OPTIONS'])
def stats():
    if request.method == 'OPTIONS':
        return make_response('', 200)
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
        print("Error stats:", str(e))
        return jsonify({"error": "server error"}), 500

@app.route('/api/user/profile', methods=['POST', 'OPTIONS'])
def user_profile():
    if request.method == 'OPTIONS':
        return make_response('', 200)
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id required"}), 400
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
        print("Error profile:", str(e))
        return jsonify({"error": "server error"}), 500

# ---------------------
# Статические файлы
# ---------------------

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# ---------------------
# Запуск
# ---------------------

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    database.init_db()
    app.run(host="0.0.0.0", port=port)














