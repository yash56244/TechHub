import os
import secrets
from PIL import Image
from main import app, db, bcrypt
from flask import redirect, render_template, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from main.forms import LoginForm, RegistrationForm, ProductForm, AddToCart
from main.models import User, Product, Cart
from werkzeug.utils import secure_filename

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                form.password.data) and user.role == form.role.data:
            session['role'] = form.role.data
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                if form.role.data == 'customer':
                    return redirect(url_for('customer_dashboard'))
                else:
                    return redirect(url_for('seller_dashboard'))
        else:
            flash('Please check your credentials', 'danger')
    return render_template('login.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = \
            bcrypt.generate_password_hash(form.password.data).decode('utf-8'
                )
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_pwd, role = form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')

@app.route('/logout')
@login_required
def logout():
    session.pop('role', None)
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard/customer')
@login_required
def customer_dashboard():
    if session['role'] == 'customer':
        products = Product.query.all()
        form = AddToCart()
        return render_template('customer_dashboard.html', products = products, form = form)
    else:
        return redirect(url_for('seller_dashboard'))

@app.route('/cart/add/<int:id>', methods = ['GET', 'POST'])
@login_required
def add_to_cart(id):
    product = Product.query.filter_by(id=id).first()
    form = AddToCart()
    if form.validate_on_submit():
        if form.quantity.data < product.quantity:
            if not Cart.query.filter_by(user_id=current_user.id).first():
                cart = Cart(products = [product], user_id = current_user.id)
                product.quantity -= form.quantity.data
                if not product.quantity_in_cart:
                    product.quantity_in_cart = form.quantity.data
                else:
                    product.quantity_in_cart += form.quantity.data
                db.session.add(cart)
                db.session.commit()
            else:
                cart = Cart.query.filter_by(user_id = current_user.id).first()
                cart.products.append(product)
                product.quantity -= form.quantity.data
                if not product.quantity_in_cart:
                    product.quantity_in_cart = form.quantity.data
                else:
                    product.quantity_in_cart += form.quantity.data
                db.session.commit()
            flash('Product successfully added to Cart', 'success')
            return redirect(url_for('cart'))
        else:
            flash('Currently {} pieces of this item are available'.format(product.quantity), 'danger')
            return redirect(url_for('customer_dashboard'))

@app.route('/cart')
@login_required
def cart():
    if session['role'] == 'customer':
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        total = 0
        for item in cart.products:
            total += item.price*item.quantity_in_cart
        return render_template('cart.html', cart = cart, total = total)
    else:
        flash('Only customer can access this page', 'warning')
        return redirect(url_for('seller_dashboard'))

@app.route('/cart/edit/<string:operation>/<int:id>')
@login_required
def edit_cart(id, operation):
    product = Product.query.filter_by(id=id).first()
    if operation == 'increase':
        if product.quantity_in_cart + 1 < product.quantity:
            product.quantity_in_cart += 1
            product.quantity -= 1
            db.session.commit()
            flash('{} quantity updated'.format(product.name), 'success')
            return redirect(url_for('cart'))
        else:
            flash('Currently {} pieces of this item are available'.format(product.quantity), 'warning')
            return redirect(url_for('cart'))
    elif operation == 'decrease':
        if product.quantity_in_cart > 1:
            product.quantity_in_cart -= 1
            product.quantity += 1
            db.session.commit()
            flash('{} quantity updated'.format(product.name), 'success')
            return redirect(url_for('cart'))
        else:
            flash('Quantity cannot be less than equal to zero', 'warning')
            return redirect(url_for('cart'))
    else:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        for item in cart.products:
            if(id == item.id):
                product.quantity += product.quantity_in_cart
                product.quantity_in_cart = 0
                cart.products.remove(item)
                db.session.commit()
                return redirect(url_for('cart'))

@app.route('/dashboard/seller')
@login_required
def seller_dashboard():
    if session['role'] == 'seller':
        products = Product.query.filter_by(seller=current_user).all()
        return render_template('seller_dashboard.html', products=products)
    else:
        return redirect(url_for('customer_dashboard'))

@app.route('/dashboard/seller/new', methods=['POST', 'GET'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name = form.name.data,
                          description = form.description.data,
                          price = form.price.data, 
                          quantity = form.quantity.data,
                          photo_name = save_picture(form.photo.data),
                          seller = current_user)
        db.session.add(product)
        db.session.commit()
        flash('Product has been added successfully!', 'success')
        return redirect(url_for('seller_dashboard'))
    return render_template('new_product.html', legend = "Add Product", form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static\product_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/product/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_product(id):
    product = Product.query.get_or_404(id)
    if product.seller != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        pathp = app.root_path + '\static\product_pics\{}'.format(product.photo_name)
        os.remove(pathp)
        product.photo_name = save_picture(form.photo.data)
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('seller_dashboard'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.quantity.data = product.quantity
    return render_template('new_product.html', legend='Update Product', form=form)
