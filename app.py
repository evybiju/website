from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "90876578909876546789887654356789087654678" # change to something very random and secret ( this is the billing's "password" key )

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'billing.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.String(50), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Admin Dashboard - Extended with more functionalities
@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    users = User.query.all()
    products = Product.query.all()
    categories = Category.query.all()
    invoices = Invoice.query.all()

    # Stats example for Admin Dashboard
    total_users = User.query.count()
    total_products = Product.query.count()
    total_sales = sum(invoice.amount for invoice in invoices)

    return render_template('admin_dashboard.html', users=users, products=products, categories=categories, invoices=invoices, 
                           total_users=total_users, total_products=total_products, total_sales=total_sales)

# Delete a user
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('admin_dashboard'))

# Edit user
@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_user.html', user=user)
    
# Edit product
@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    product = Product.query.get(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.description = request.form['description']
        product.category_id = request.form['category_id']
        db.session.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_product.html', product=product, categories=categories)

# Delete product
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully.", "success")
    else:
        flash("Product not found.", "danger")
    return redirect(url_for('admin_dashboard'))
    
# Delete category (ensure no products are assigned to the category)
@app.route('/admin/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    category = Category.query.get(category_id)
    if category and not category.products:  # Check if the category has any products assigned
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully.", "success")
    else:
        flash("Cannot delete category. It has products assigned.", "danger")
    return redirect(url_for('admin_dashboard'))


# Add a new category
@app.route('/admin/add_category', methods=['GET', 'POST'])
def add_category():
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        category_name = request.form['name']
        new_category = Category(name=category_name)
        db.session.add(new_category)
        try:
            db.session.commit()
            flash("Category added successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        except:
            db.session.rollback()
            flash("Error adding category. It may already exist.", "danger")

    return render_template('add_category.html')

# Add a new product
@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' not in session or session['username'] != 'admin':
        flash("Access restricted to admin only.", "danger")
        return redirect(url_for('login'))

    categories = Category.query.all()
    if request.method == 'POST':
        product_name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category_id = request.form['category_id']

        new_product = Product(name=product_name, price=price, description=description, category_id=category_id)
        db.session.add(new_product)
        try:
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        except:
            db.session.rollback()
            flash("Error adding product. It may already exist.", "danger")

    return render_template('add_product.html', categories=categories)

# Products Page (Main Page with category selection)
@app.route('/products', methods=['GET', 'POST'])
def products():
    categories = Category.query.all()
    selected_category_id = request.form.get('category_id')

    if selected_category_id:
        products = Product.query.filter_by(category_id=selected_category_id).all()
    else:
        products = []

    return render_template('products.html', categories=categories, products=products, selected_category_id=selected_category_id)

# Home route (Login or Dashboard based on session)
@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html')
    return render_template('index.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('Username already exists!', 'danger')

    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')

# User Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    invoices = Invoice.query.filter_by(user_id=user_id).all()

    return render_template('dashboard.html', invoices=invoices)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5454, debug=True)
