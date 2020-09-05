from main import app, db, bcrypt
from flask import redirect, render_template, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from main.forms import LoginForm, RegistrationForm
from main.models import User, Product
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
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
        flash('Your account has been created! Please Login', 'success')
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
        return render_template('customer_dashboard.html')
    else:
        return redirect(url_for('seller_dashboard'))

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
    if request.method == 'POST':
        product = Product(name = request.form.get('name'),
                          description = request.form.get('description'),
                          price = request.form.get('price'), 
                          quantity = request.form.get('quantity'), 
                          photo = request.files['inputPhoto'].read(),
                          seller = current_user)
        db.session.add(product)
        db.session.commit()
        flash('Product has been added successfully!', 'success')
        return redirect(url_for('seller_dashboard'))
    return render_template('new_product.html', legend = "Add Product")

@app.route('/product/<int:id>/photo')
@login_required
def product_photo(id):
    product = Product.query.get_or_404(id)
    return app.response_class(product.photo, mimetype='application/octet-stream')