from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Change in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created before the app runs
    app.run(debug=True)



# --------------------
# Register Route
# --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# --------------------
# Login Route
# --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)


# --------------------
# Dashboard (Protected)
# --------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


# --------------------
# Logout
# --------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# --------------------
# Home Route (Optional)
# --------------------
@app.route('/')
def home():
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
