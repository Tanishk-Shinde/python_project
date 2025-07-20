import sqlite3

def init_db():
    conn = sqlite3.connect('database/users.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        type TEXT,
        grammar_score REAL,
        readability_score REAL,
        final_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def insert_user(username, password_hash):
    try:
        conn = sqlite3.connect('database/users.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_user_by_username(username):
    conn = sqlite3.connect('database/users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user

def save_result(user_id, filename, data):
    conn = sqlite3.connect('database/users.db')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO results (user_id, filename, type, grammar_score, readability_score, final_score)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, filename, data.get('type'), data.get('grammar_score'), data.get('readability_score', 0), data.get('final_score')))
    conn.commit()
    conn.close()
def get_user_by_id(user_id):
    conn = sqlite3.connect('database/users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user
