# webapp.py
from flask import Flask, request, jsonify, send_from_directory, make_response
import database
import os

app = Flask(__name__, static_folder='static')

# УБРАЛИ: from flask_cors import CORS — не нужен, если делаем CORS вручную

# ---------------------
# РУЧНОЙ CORS (для WebApp в Telegram)
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
        # Возвращаем пустой ответ с нужными заголовками
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        return response

# ---------------------
# API Маршруты
# ---------------------

@app.route('/api/user/actions', methods=['POST'])
def user_actions():
    print("🔹 [DEBUG] POST /api/user/actions — запрос получен")
    print("🔹 [DEBUG] Заголовки:", dict(request.headers))
    print("🔹 [DEBUG] Тело запроса:", request.json)
    
    user_id = request.json.get('user_id')
    if not user_id:
        print("🔸 Ошибка: user_id не передан")
        return jsonify({"error": "user_id required"}), 400

    try:
        actions = database.get_user_actions(user_id)
        print(f"🔹 [DEBUG] Найдено действий: {len(actions)}")
        return jsonify(actions)
    except Exception as e:
        print("🔸 Ошибка при получении действий:", str(e))
        return jsonify({"error": "server error"}), 500

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
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print("🔸 Ошибка profile:", str(e))
        return jsonify({"error": "server error"}), 500

@app.route('/api/admin/actions', methods=['GET'])
def admin_actions():
    tg_user_id = request.args.get('user_id')
    admin_id = int(os.getenv("ADMIN_ID", 0))
    if not tg_user_id or int(tg_user_id) != admin_id:
        return jsonify({"error": "Access denied"}), 403
    try:
        return jsonify(database.get_all_actions())
    except Exception as e:
        print("🔸 Ошибка admin:", str(e))
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
# Запуск сервера
# ---------------------

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))  # Railway использует 8080
    database.init_db()
    app.run(host="0.0.0.0", port=port)












