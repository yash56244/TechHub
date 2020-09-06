from main import db, app, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text(15), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    products = db.relationship('Product', backref='seller', lazy=True)
    cart_items = db.relationship('Product', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text(20), nullable=False)
    description = db.Column(db.Text(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    quantity_in_cart = db.Column(db.Integer, nullable = True)
    photo_name = db.Column(db.Text, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable = True)

    def __repr__(self):
        return f"Product('{self.name}','{self.seller_id}', '{self.quantity}')"

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    products = db.relationship('Product', backref='cartItems', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
