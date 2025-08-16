# webapp.py
# webapp.py
from flask import Flask, request, jsonify, send_from_directory, make_response
import database
import os

app = Flask(__name__, static_folder='static')

# ---------------------
# РУЧНОЙ CORS — КРИТИЧЕСКИ ВАЖНО ДЛЯ TELEGRAM WEBAPP
# ---------------------

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        # Явно возвращаем 200 OK
        response = make_response('', 200)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        return response

# ---------------------
# API: действия пользователя
# ---------------------

@app.route('/api/user/actions', methods=['POST'])
def user_actions():
    print("🔹 [DEBUG] POST /api/user/actions — запрос получен")
    user_id = request.json.get('user_id')
    if not user_id:
        print("🔸 Ошибка: user_id не передан")
        return jsonify({"error": "user_id required"}), 400
    try:
        actions = database.get_user_actions(user_id)
        print(f"🔹 [DEBUG] Отправлено {len(actions)} действий")
        return jsonify(actions)
    except Exception as e:
        print("🔸 Ошибка:", str(e))
        return jsonify({"error": "server error"}), 500

# ---------------------
# API: статистика
# ---------------------

@app.route('/api/stats', methods=['GET'])
def stats():
    print("🔹 [DEBUG] GET /api/stats — запрос получен")
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
        print("🔸 Ошибка stats:", str(e))
        return jsonify({"error": "server error"}), 500

# ---------------------
# API: профиль
# ---------------------

@app.route('/api/user/profile', methods=['POST'])
def user_profile():
    print("🔹 [DEBUG] POST /api/user/profile — запрос получен")
    user_id = request.json.get('user_id')
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
        print("🔸 Ошибка profile:", str(e))
        return jsonify({"error": "server error"}), 500

# ---------------------
# Админка
# ---------------------

@app.route('/api/admin/actions', methods=['GET'])
def admin_actions():
    tg_user_id = request.args.get('user_id')
    admin_id = int(os.getenv("ADMIN_ID", 0))
    if not tg_user_id or int(tg_user_id) != admin_id:
        return jsonify({"error": "Access denied"}), 403
    return jsonify(database.get_all_actions())

# ---------------------
# Статика
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













