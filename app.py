from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATABASE = 'users.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute("SELECT COUNT(*) as count FROM users")
        if cursor.fetchone()['count'] == 0:
            cursor.execute("INSERT INTO users (username, password, full_name, email) VALUES (?, ?, ?, ?)",
                           ('admin', 'admin123', 'Администратор', 'admin@example.com'))
            cursor.execute("INSERT INTO users (username, password, full_name, email) VALUES (?, ?, ?, ?)",
                           ('user1', 'password1', 'Иван Петров', 'ivan@example.com'))
            cursor.execute("INSERT INTO users (username, password, full_name, email, status) VALUES (?, ?, ?, ?, ?)",
                           ('user2', 'password2', 'Мария Сидорова', 'maria@example.com', 'inactive'))
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', user=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Окно авторизации"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        if user:
            if user['status'] == 'active':
                session['username'] = username
                session['user_id'] = user['id']
                flash(f'Добро пожаловать, {username}!', 'success')
                return redirect(url_for('profile'))
            elif user['status'] == 'inactive':
                flash('Ваш аккаунт неактивен. Обратитесь к администратору.', 'warning')
            elif user['status'] == 'blocked':
                flash('Ваш аккаунт заблокирован.', 'danger')
        else:
            flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Окно регистрации"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form.get('full_name', '')
        email = request.form.get('email', '')
        
        if not username or not password:
            flash('Логин и пароль обязательны для заполнения', 'warning')
            return render_template('register.html')
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, password, full_name, email) VALUES (?, ?, ?, ?)",
                           (username, password, full_name, email))
            db.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким именем уже существует', 'danger')
    
    return render_template('register.html')

@app.route('/profile')
def profile():
    """Личная страница пользователя"""
    if 'username' not in session:
        flash('Для просмотра профиля необходимо войти в систему', 'warning')
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    if not user:
        session.clear()
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    username = session.get('username', 'Гость')
    session.clear()
    flash(f'До свидания, {username}! Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
