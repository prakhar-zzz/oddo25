from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from models import db, User, Item, Swap
from forms import LoginForm, ItemForm  # Ensure your forms file exists and includes LoginForm and ItemForm

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Replace with environment variable in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    featured_items = Item.query.filter_by(approved=True, available=True).limit(4).all()
    return render_template('home.html', featured_items=featured_items)


@app.route('/browse')
def browse():
    items = Item.query.filter_by(approved=True, available=True).all()
    return render_template('browse.html', items=items)


@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        new_item = Item(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            type=form.type.data,
            size=form.size.data,
            condition=form.condition.data,
            tags=form.tags.data,
            user_id=current_user.id,
            available=True,
            approved=False
        )
        db.session.add(new_item)
        db.session.commit()
        flash("Item submitted for review.", "info")
        return redirect(url_for('dashboard'))
    return render_template('add_item.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))  # ✅ Fixed redirection
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    my_items = Item.query.filter_by(user_id=current_user.id).all()
    my_swaps = Swap.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, items=my_items, swaps=my_swaps)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/swap_request/<int:item_id>', methods=['POST'])
@login_required
def swap_request(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        flash("You can't request your own item.", 'warning')
        return redirect(url_for('dashboard'))

    if not item.available or not item.approved:
        flash("Item not available.", 'danger')
        return redirect(url_for('dashboard'))

    existing = Swap.query.filter_by(user_id=current_user.id, item_id=item_id, status='pending').first()
    if existing:
        flash("Already requested.", 'info')
        return redirect(url_for('dashboard'))

    swap = Swap(
        user_id=current_user.id,
        item_id=item.id,
        swap_type='swap',
        status='pending',
        timestamp=datetime.utcnow()
    )
    db.session.add(swap)
    db.session.commit()
    flash("Swap request sent.", 'success')
    return redirect(url_for('dashboard'))


@app.route('/redeem/<int:item_id>', methods=['POST'])
@login_required
def redeem_with_points(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        flash("You can't redeem your own item.", 'warning')
        return redirect(url_for('dashboard'))

    if not item.available or not item.approved:
        flash("Item not available.", 'danger')
        return redirect(url_for('dashboard'))

    if current_user.points < 50:
        flash("Not enough points.", 'danger')
        return redirect(url_for('dashboard'))

    current_user.points -= 50
    item.available = False

    swap = Swap(
        user_id=current_user.id,
        item_id=item.id,
        swap_type='points',
        status='completed',
        timestamp=datetime.utcnow()
    )
    db.session.add(swap)
    db.session.commit()
    flash("Item redeemed via points!", 'success')
    return redirect(url_for('dashboard'))


@app.route('/my_swap_requests')
@login_required
def my_swap_requests():
    my_items = Item.query.filter_by(user_id=current_user.id).all()
    item_ids = [item.id for item in my_items]
    requests = Swap.query.filter(Swap.item_id.in_(item_ids), Swap.status == 'pending').all()
    return render_template('swap_requests.html', requests=requests)


@app.route('/swap_action/<int:swap_id>/<string:action>', methods=['POST'])
@login_required
def handle_swap(swap_id, action):
    swap = Swap.query.get_or_404(swap_id)
    item = swap.item
    if item.user_id != current_user.id:
        flash("Unauthorized.", 'danger')
        return redirect(url_for('my_swap_requests'))

    if action == 'approve':
        swap.status = 'completed'
        item.available = False
        swap.user.points += 50
    elif action == 'decline':
        swap.status = 'declined'
    else:
        flash("Invalid action.", 'danger')
        return redirect(url_for('my_swap_requests'))

    db.session.commit()
    flash(f"Swap {action}d successfully.", 'success')
    return redirect(url_for('my_swap_requests'))

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('itemlisting.html', item=item)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
