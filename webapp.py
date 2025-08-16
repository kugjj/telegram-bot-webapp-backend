# webapp.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS 
import database
import os
app = Flask(__name__, static_folder='static')
CORS(app)    # Разрешает запросы с любого домена
app = Flask(__name__, static_folder='static')

@app.route('/api/user/actions', methods=['POST'])
def user_actions():
    print("🔹 [DEBUG] Получен запрос на /api/user/actions")
    print("🔹 [DEBUG] JSON тело:", request.json)
    user_id = request.json.get('user_id')
    if not user_id:
        print("🔸 Ошибка: user_id не передан")
        return jsonify({"error": "user_id required"}), 400
    actions = database.get_user_actions(user_id)
    print(f"🔹 [DEBUG] Найдено действий для {user_id}: {len(actions)}")
    return jsonify(actions)

@app.route('/api/user/actions', methods=['POST'])
def user_actions():
    user_id = request.json.get('user_id')
    actions = database.get_user_actions(user_id)
    return jsonify(actions)

@app.route('/api/admin/actions', methods=['GET'])
def admin_actions():
    tg_user_id = request.args.get('user_id')
    admin_id = int(os.getenv("ADMIN_ID", 0))
    if not tg_user_id or int(tg_user_id) != admin_id:
        return jsonify({"error": "Access denied"}), 403
    return jsonify(database.get_all_actions())

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

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

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    database.init_db()

    app.run(host="0.0.0.0", port=port)



