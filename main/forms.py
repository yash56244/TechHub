from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, \
    BooleanField, TextAreaField, RadioField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, \
    ValidationError, EqualTo
from main.models import User

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    role = StringField('Role', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired()])
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

class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    addToCart = SubmitField('Add To Cart')

class AddressForm(FlaskForm):
    addressLine1 = TextAreaField('Address Line 1', validators=[DataRequired()])
    addressLine2 = TextAreaField('Address Line 2', validators=[DataRequired()])
    pincode = IntegerField('Pin-Code', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    mobile = IntegerField('Mobile No.', validators=[DataRequired()])
    submit = SubmitField('Place Order')

    def validate_mobile(self, mobile):
        if(len(str(mobile.data))) != 10:
            raise ValidationError('Mobile Number must contain 10 digits.')
    
    def validate_pincode(self, pincode):
        if(len(str(pincode.data))) != 6:
            raise ValidationError('Please enter a valid 6 digit Pin-Code')