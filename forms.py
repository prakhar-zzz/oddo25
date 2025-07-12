from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    category = SelectField('Category', choices=[
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('dresses', 'Dresses'),
        ('outerwear', 'Outerwear'),
        ('accessories', 'Accessories')
    ], validators=[DataRequired()])
    type = SelectField('Type', choices=[
        ('swap', 'Swap'),
        ('donate', 'Donate')
    ], validators=[DataRequired()])
    size = StringField('Size', validators=[DataRequired(), Length(max=10)])
    condition = SelectField('Condition', choices=[
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('used', 'Used'),
        ('worn', 'Worn')
    ], validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)', validators=[Length(max=100)])
    submit = SubmitField('List Item')
