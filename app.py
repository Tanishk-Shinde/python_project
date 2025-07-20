from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import sqlite3
import os
import base64
from werkzeug.utils import secure_filename
import time
from werkzeug.security import generate_password_hash

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    # Check if email already exists
    cur.execute("SELECT id, email FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        user = User(id=row[0], email=row[1])
    else:
        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
        conn.commit()
        user_id = cur.lastrowid
        user = User(id=user_id, email=email)
    conn.close()
    login_user(user)
    return redirect(url_for('home'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/main')
@login_required
def main():
    return render_template('main.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    user_id = str(current_user.id)
    timestamp = int(time.time())
    unique_filename = f"{user_id}_{timestamp}_{filename}"
    save_path = os.path.join('uploads', unique_filename)
    file.save(save_path)
    return jsonify({'success': True, 'filename': unique_filename}), 200

@app.route('/upload_audio', methods=['POST'])
@login_required
def upload_audio():
    audio_data = request.form.get('audio_data')
    if not audio_data:
        return jsonify({'success': False, 'error': 'No audio data'}), 400
    header, encoded = audio_data.split(',', 1)
    audio_bytes = base64.b64decode(encoded)
    user_id = str(current_user.id)
    timestamp = int(time.time())
    filename = f"{user_id}_{timestamp}_recorded_pitch.webm"
    save_path = os.path.join('uploads', filename)
    with open(save_path, 'wb') as f:
        f.write(audio_bytes)
    return jsonify({'success': True, 'filename': filename}), 200

if __name__ == '__main__':
    app.run(debug=True)