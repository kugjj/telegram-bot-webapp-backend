# webapp.py
from flask import Flask, request, jsonify, send_from_directory
import database
import os

app = Flask(__name__, static_folder='static')

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

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    database.init_db()
    app.run(host="0.0.0.0", port=port)