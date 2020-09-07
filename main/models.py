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
    addressess = db.relationship('Address', backref='customer', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text(20), nullable=False)
    description = db.Column(db.Text(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    photo_name = db.Column(db.Text, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    seller_order_id = db.Column(db.Integer, db.ForeignKey('sellerorder.id'))

    def __repr__(self):
        return f"Product('{self.name}','{self.seller_id}', '{self.quantity}')"

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.relationship('Product', backref='productc', uselist=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product = db.relationship('Product', backref='producto', uselist=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

class Sellerorder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product = db.relationship('Product', backref='productso', uselist=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    addressLine1 = db.Column(db.Text(50), nullable=False)
    addressLine2 = db.Column(db.Text(50), nullable=False)
    pincode = db.Column(db.Integer, nullable = False)
    city = db.Column(db.String(15), nullable = False)
    state = db.Column(db.String(20), nullable = False)
    mobile = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Address('{self.addressLine1}', '{self.addressLine2}', '{self.pincode}', '{self.city}', '{self.state}')"