import os
import secrets
from PIL import Image
from main import app, db, bcrypt
from flask import redirect, render_template, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from main.forms import LoginForm, RegistrationForm, ProductForm, AddToCart, AddressForm
from main.models import User, Product, Cart, Order, Address, Sellerorder
from werkzeug.utils import secure_filename

@app.route('/', methods=['GET', 'POST'])
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
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                if form.role.data == 'customer':
                    return redirect(url_for('customer_home'))
                else:
                    return redirect(url_for('seller_dashboard'))
        else:
            flash('Please check your credentials', 'error_outline')
    return render_template('login.html', form=form, title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = \
            bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_pwd, role = form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'check')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')

@app.route('/logout')
@login_required
def logout():
    session.pop('role', None)
    logout_user()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if session['role'] == 'customer':
        if request.method == 'POST':
            query = request.form.get('search')
            products = Product.query
            products = products.filter(Product.name.like('%' + query + '%'))
            products = products.order_by(Product.name).all()
            return render_template('search.html', products=products, query=query)
        else:
            return redirect(url_for('customer_home'))
    else:
        return redirect(url_for('seller_dashboard'))

@app.route('/products')
@login_required
def products():
    if session['role'] == 'customer':
        products = Product.query.all()
        return render_template('products.html', products = products)
    else:
        return redirect(url_for('seller_dashboard'))

@app.route('/products/seller/<int:id>')
@login_required
def seller_products(id):
    products = Product.query.filter_by(seller_id=id).all()
    seller = User.query.filter_by(id = id).first()
    return render_template('products.html', products = products, name = seller.username)

@app.route('/product/<int:id>')
@login_required
def show_product(id):
    if session['role'] == 'customer':
        product = Product.query.filter_by(id=id).first()
        seller = User.query.filter_by(id = product.seller_id).first()
        form = AddToCart()
        return render_template('show_product.html', product = product, form = form, seller = seller)
    else:
        return redirect(url_for('seller_dashboard'))

@app.route('/customer/home')
@login_required
def customer_home():
    if session['role'] == 'customer':
        products = Product.query.all()
        form = AddToCart()
        return render_template('customer_home.html', products = products[:4], form = form)
    else:
        return redirect(url_for('seller_dashboard'))

@app.route('/customer/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=orders)

@app.route('/customer/cart')
@login_required
def cart():
    if session['role'] == 'customer':
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        total = 0
        for item in cart:
            total += item.product.price*item.quantity
        return render_template('cart.html', cart = cart, total = total)
    else:
        flash('Only customer can access this page', 'warning')
        return redirect(url_for('seller_dashboard'))

@app.route('/customer/cart/add/<int:id>', methods = ['GET', 'POST'])
@login_required
def add_to_cart(id):
    product = Product.query.filter_by(id=id).first()
    form = AddToCart()
    if form.validate_on_submit:
        if form.quantity.data < product.quantity:
            cart = Cart.query.filter_by(user_id=current_user.id).all()
            alreadyPresent=False
            for c in cart:
                if product.id == c.product.id:
                    c.quantity += form.quantity.data
                    db.session.commit()
                    alreadyPresent=True
                    break
            if not alreadyPresent:
                cart1 = Cart(product = product, user_id=current_user.id, quantity=form.quantity.data)
                db.session.add(cart1)
                db.session.commit()
            flash('Product successfully added to Cart', 'check')
            return redirect(url_for('cart'))
        else:
            flash('Currently {} pieces of this item are available'.format(product.quantity), 'error_outline')
            return redirect(url_for('customer_home'))

@app.route('/customer/cart/<string:operation>/<int:id>')
@login_required
def edit_cart(id, operation):
    cart = Cart.query.filter_by(id=id).first()
    if operation == 'increase':
        if cart.quantity < cart.product.quantity:
            cart.quantity += 1
            db.session.commit()
            flash('{} quantity updated'.format(cart.product.name), 'check')
            return redirect(url_for('cart'))
        else:
            flash('Currently {} pieces of this item are available'.format(cart.product.quantity), 'warning')
            return redirect(url_for('cart'))
    elif operation == 'decrease':
        if cart.quantity > 1:
            cart.quantity -= 1
            db.session.commit()
            flash('{} quantity updated'.format(cart.product.name), 'check')
            return redirect(url_for('cart'))
        else:
            flash('Quantity cannot be less than one.', 'warning')
            return redirect(url_for('cart'))
    else:
        db.session.delete(cart)
        db.session.commit()
        flash('Item removed successfully', 'check')
        return redirect(url_for('cart'))

@app.route('/dashboard/seller')
@login_required
def seller_dashboard():
    if session['role'] == 'seller':
        products = Product.query.filter_by(seller=current_user).all()
        return render_template('seller_dashboard.html', products=products)
    else:
        return redirect(url_for('customer_home'))

@app.route('/dashboard/seller/history')
@login_required
def seller_history():
    seller_orders = Sellerorder.query.filter_by(seller_id = current_user.id).all()
    customers = []
    for seller_order in seller_orders:
        customer_id = seller_order.user_id
        customer = User.query.filter_by(id=customer_id).first()
        customers.append(customer)
    return render_template('seller_history.html',context = zip(seller_orders, customers))

@app.route('/dashboard/seller/new_product', methods=['POST', 'GET'])
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
        flash('Product has been added successfully!', 'check')
        return redirect(url_for('seller_dashboard'))
    return render_template('new_product.html', legend = "Add Product", form=form)

def save_picture(form_picture):
    if form_picture:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static\product_pics', picture_fn)

        output_size = (250, 250)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)

        return picture_fn

@app.route('/seller/product/<int:id>/update', methods=['GET', 'POST'])
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
        flash('Product has been updated!', 'check')
        return redirect(url_for('seller_dashboard'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.quantity.data = product.quantity
    return render_template('new_product.html', legend='Update Product', form=form)

@app.route('/customer/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = AddressForm()
    cart = Cart.query.filter_by(user_id=current_user.id).all()
    address = Address.query.filter_by(user_id=current_user.id).first()
    total = 0
    for item in cart:
        total += item.product.price*item.quantity
    if form.validate_on_submit():
        if address is None:
            address = Address(addressLine1 = form.addressLine1.data,
                            addressLine2 = form.addressLine2.data,
                            pincode = form.pincode.data,
                            city = form.city.data,
                            state = form.state.data,
                            mobile = form.mobile.data,
                            customer = current_user)
            db.session.add(address)
            db.session.commit()
        for item in cart:
            order = Order(product = item.product, user_id = current_user.id, quantity=item.quantity, total = total)
            db.session.add(order)
            db.session.commit()
        for item in cart:
            sellerOrder = Sellerorder(seller_id=item.product.seller_id, user_id = current_user.id, product = item.product, quantity=item.quantity, total = total)
            db.session.add(sellerOrder)
            db.session.commit()
        for item in cart:
            product = Product.query.filter_by(id=item.product.id).first()
            product.quantity -= item.quantity
            db.session.commit()
        for item in cart:
            Cart.query.filter_by(id=item.id).delete()
            db.session.commit()
        flash('Order Placed successfully', 'check')
        return redirect(url_for('orders'))
    if request.method == 'GET' and address is not None:
        form.addressLine1.data = address.addressLine1
        form.addressLine2.data = address.addressLine2
        form.pincode.data = address.pincode
        form.city.data = address.city
        form.state.data = address.state
        form.mobile.data = address.mobile
    return render_template('checkout.html', form=form, total=total, cart_items=cart)
