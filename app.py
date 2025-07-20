from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- Setup Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)

# --- Dummy User Class for Demo ---
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(id=row[0], email=row[1])
    return None

# --- Routes ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    # Check if email exists in DB
    cur.execute("SELECT id, email FROM users WHERE email = ?", (email,))
    row = cur.fetchone()

    if row:
        user = User(id=row[0], email=row[1])
    else:
        # Register new user if not exists
        cur.execute("INSERT INTO users (email) VALUES (?)", (email,))
        conn.commit()
        user_id = cur.lastrowid
        user = User(id=user_id, email=email)

    conn.close()
    login_user(user)
    return redirect(url_for('main'))

@app.route('/main')
@login_required
def main():
    return "Welcome to PitchPerfect!"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
from utils.analysis_engine import analyze_pitch
from utils.db_utils import init_db, insert_user, get_user_by_username, save_result