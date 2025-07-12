from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Set absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Example model (replace with your actual imports if needed)
class Dummy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

with app.app_context():
    db.create_all()
    print(f"Database created at: {db_path}")
