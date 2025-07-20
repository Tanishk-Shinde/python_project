from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from utils.db_utils import init_db, get_user_by_username, insert_user, get_user_by_id
from flask_login import current_user
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- Setup Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

# --- User Class ---
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return User(id=user[0], username=user[1])
    return None

# --- Routes ---

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = get_user_by_username(username)
    
    if user and check_password_hash(user[2], password):
        login_user(User(id=user[0], username=user[1]))
        return redirect(url_for('main'))
    else:
        flash("Invalid username or password.")
        return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        if get_user_by_username(username):
            flash("Username already exists.")
            return redirect(url_for('signup'))

        if insert_user(username, password_hash):
            flash("Account created. Please log in.")
            return redirect(url_for('index'))
        else:
            flash("Error: Could not create user.")
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.route('/main')
@login_required
def main():
    return render_template('main.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
