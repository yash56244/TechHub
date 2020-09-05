from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, \
    BooleanField, TextAreaField, RadioField, IntegerField
from wtforms.validators import DataRequired, Length, Email, \
    ValidationError, EqualTo
from main.models import User

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    role = RadioField('Role', choices = [('customer', 'Customer'), ('seller', 'Seller')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    role = RadioField('Role', choices = [('customer', 'Customer'), ('seller', 'Seller')], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(),
                           Length(min=4, max=15)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Confirm Password',
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exists')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exists')
    
    def validate_password(self, password):
        if not any(char.isdigit() for char in password.data): 
            raise ValidationError('Password should have at least one number')
            
        if not any(char.isupper() for char in password.data): 
            raise ValidationError('Password should have at least one uppercase letter')
            
        if not any(char.islower() for char in password.data): 
            raise ValidationError('Password should have at least one lowercase letter')

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    add_product = SubmitField('Add/Update Product')

    def validate_price(self, price):
        if price.data <= 0:
            raise ValidationError('Price must be greater than zero.')

    def validate_quantity(self, quantity):
        if quantity.data < 0:
            raise ValidationError('Quantity must be greater than zero.')