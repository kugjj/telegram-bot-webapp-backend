# database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "dbname=botdb user=postgres password=pass host=localhost")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, username, first_name, last_name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (user_data['id'], user_data['username'], user_data['first_name'], user_data['last_name']))
    conn.commit()
    conn.close()

def log_action(user_id, action):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO actions (user_id, action) VALUES (%s, %s)", (user_id, action))
    conn.commit()
    conn.close()

def get_user_actions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT action, timestamp FROM actions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"action": r["action"], "time": r["timestamp"]} for r in rows]

def get_all_actions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, a.action, a.timestamp 
        FROM actions a 
        JOIN users u ON a.user_id = u.id 
        ORDER BY a.timestamp DESC LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"user": r["username"], "action": r["action"], "time": r["timestamp"]} for r in rows]