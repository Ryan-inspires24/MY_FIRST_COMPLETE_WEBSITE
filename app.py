from flask import Flask, render_template, request, redirect, flash, jsonify, url_for, abort, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
import requests
from flask_login import LoginManager
from flask_login import current_user, logout_user, login_required, LoginManager, login_user
from datetime import timedelta
from sqlalchemy.ext.hybrid import hybrid_property
import traceback
import os
 
app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

@app.before_request
def make_session_permanent():
    session.permanent = True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ryan_inspires:Asherinyuy24@localhost/caminspo_db'
app.secret_key = 'Gxo/24#9' 
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return Clients.query.get(int(user_id))
 
db = SQLAlchemy(app)
 
# Product Categories
class ProductCategories(db.Model):
    __tablename__ = 'product_categories'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=True)

    # Relationships
    user = db.relationship('User', backref='comments_made', foreign_keys=[user_id]) 
    vendor = db.relationship('User', back_populates='comments_received', foreign_keys=[vendor_id])
    product = db.relationship('Product', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'
     

class FavoriteVendor(db.Model):
    __tablename__ = 'favorite_vendors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # user who favorited the vendor
    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='favorite_vendors'
    )

    # vendor being favorited
    vendor = db.relationship(
        'User',
        foreign_keys=[vendor_id],
        back_populates='favorited_by',
        primaryjoin='FavoriteVendor.vendor_id == User.id'
    )

    def __repr__(self):
        return f'<FavoriteVendor user={self.user_id} vendor={self.vendor_id}>'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50))  # 'vendor' or 'client'

    # For Vendors
    first_name = db.Column(db.String(50), nullable=True)
    surname = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)

    # Relationships
    favorite_vendors = db.relationship(
        'FavoriteVendor',
        foreign_keys=[FavoriteVendor.user_id],
        back_populates='user',
        cascade='all, delete-orphan'
    )

    favorited_by = db.relationship(
        'FavoriteVendor',
        foreign_keys=[FavoriteVendor.vendor_id],
        back_populates='vendor',
        cascade='all, delete-orphan'
    )
    
    saved_products = db.relationship(
        'SavedProduct',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    
    comments_received = db.relationship(
        'Comment',
        back_populates='vendor',
        foreign_keys=[Comment.vendor_id]
    )

    products = db.relationship('Product', back_populates='vendor', lazy=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

    @property
    def is_vendor(self):
        return self.role == 'vendor'

    @property
    def is_client(self):
        return self.role == 'client'


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    product_pic = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.category_id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor = db.relationship('User', back_populates='products')
    category = db.relationship('ProductCategories', backref="products")
    comments = db.relationship('Comment', back_populates='product', lazy=True)

class SavedProduct(db.Model):
    __tablename__ = 'saved_products'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)

    user = db.relationship('User', back_populates='saved_products')
    product = db.relationship('Product')

    def __repr__(self):
        return f'<SavedProduct user={self.user_id} product={self.product_id}>'


@app.route('/me_page/<int:vendor_id>')
def me_page(vendor_id):

    if current_user.id != vendor_id:
        return f'unauthorized' 

    vendor = User.query.filter_by(id=vendor_id, role='vendor').first_or_404()
    products = Product.query.filter_by(vendor_id=vendor_id).all()
    return render_template('me_page.html', vendor=vendor, products=products)

 
 
@app.route('/db_setup')
def db_setup():
         db.create_all() 
         return 'CamInspo Database successfully created!'
 
 
@app.route('/vendors.html')
def vendors_page():
     vendors = Vendor.query.all()  
     return render_template('vendors.html', vendors=vendors)
 
@app.route('/products.html')
def products_page():
     products = Product.query.all()  
     return render_template("products.html", products=products)
 
@app.route('/product/<int:product_id>')
def product_details(product_id):
     product = Product.query.get(product_id)  
     if product:
         return render_template("product_details.html", product=product)
     return "Product not found", 404
 
@app.route('/vendor/<int:vendor_id>')
def vendor_profile(vendor_id):
     vendor = Vendor.query.get(vendor_id)
     if not vendor:
         abort(404) 
     return render_template("vendor_profile.html", vendor=vendor)
 
@app.route('/about.html')
def about_page():
     return render_template('about.html')
 
 
@app.route('/api/check_username')
def check_username():
    username = request.args.get('username', '').strip()
    role = request.args.get('role', '').strip()  # Get the selected role from the query params

    if not username:
        return jsonify({'available': False, 'error': 'Username required'}), 400

    if not role:
        return jsonify({'available': False, 'error': 'User role required'}), 400

    # Check if a user with the same username and role already exists
    exists = db.session.query(User.id).filter_by(username=username, role=role).first() is not None

    return jsonify({'available': not exists})
@app.route('/api/add_comment', methods=['POST'])
def add_comment():
    try:
        data = request.get_json()
        content = data.get('content')
        vendor_id = data.get('vendor_id')

        if not content:
            return jsonify({'success': False, 'error': 'Comment content is required.'}), 400

        # Ensure user is authenticated
        # if not current_user.is_authenticated:
        #     return jsonify({'success': False, 'error': 'You must be logged in to comment.'}), 401

        user_id = current_user.id

        is_vendor = Vendors.query.get(user_id)
        is_client = Clients.query.get(user_id)

        if not is_vendor and not is_client:
            return jsonify({'success': False, 'error': 'Only registered vendors or clients can comment.'}), 403

        # Check if the vendor being commented on exists
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return jsonify({'success': False, 'error': 'Vendor does not exist.'}), 400

        # Create new comment
        new_comment = Comment(content=content, user_id=user_id, vendor_id=vendor_id)
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'content': content,
            'user_id': user_id,
            'created_at': new_comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
         print("Error occurred:", e) 
         return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/resetdb')
def resetdb():
    db.drop_all()
    db.create_all()
    return 'Database reset successfully'
    

 
@app.route('/api/register', methods=['POST'])
def api_register():

    user_type = request.form.get('user_type')
    first_name = request.form.get('first_name')
    surname = request.form.get('surname')
    username =request.form.get('register_username')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    password = request.form.get('register_password')
    profile_picture = request.files.get('profile_picture')

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    # Handle profile picture upload
    if profile_picture:
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join('static', 'vendor_images', filename))
        else:
            return jsonify({"message": "Invalid file type for profile picture!"}), 400
    else:
        filename = None  

    if user_type == 'client':
        new_user = User(
            username=username,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
            role='client'
        )
    elif user_type == 'vendor':
        description = request.form.get('description')
        new_user = User(
            username=username,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
            first_name=first_name,
            surname=surname,
            profile_picture=filename,
            description=description,
            role='vendor'
        )
    else:
        return jsonify({"message": "Invalid user type!"}), 400

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Registration successful!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500
 
  
@app.route('/check_email')
def check_email():
     email = request.args.get('email')
     if not email:
         return jsonify({'available': False})
 
@app.route('/add_product', methods=['POST'])
def add_product():
     try:
         product_name = request.form['product_name']
         description = request.form['description']
         price = float(request.form['price'])
         vendor_id = int(request.form['vendor_id'])
         category_id = int(request.form['category']) 
 
 
         product_pic = request.files.get('product_pic')
         image_filename = None
 
         if product_pic and product_pic.filename != '':
             filename = secure_filename(product_pic.filename)
             
             image_path = os.path.join(app.root_path, 'static', 'product_images', filename)
             product_pic.save(image_path)
             
             image_filename = filename
 
         new_product = Products(
             product_name=product_name,
             description=description,
             price=price,
             vendor_id=vendor_id,
             product_pic=image_filename,
             category_id = category_id
         )
 
         db.session.add(new_product)
         db.session.commit()
 
         img_url = url_for('static', filename='product_images/' + image_filename) if image_filename else ''
         print("Product Name:", product_name)
         print("Price:", price)
         print("Image Filename:", image_filename)
 
         return jsonify({
             'success': True,
             'product_name': product_name,
             'price': price,
             'img_url': img_url
         }),200
 
     except Exception as e:
         print("Error adding product:", e)
         print(traceback.format_exc())  
 
         return jsonify({'success': False, 'error': str(e)}), 500
                 


@app.route('/api/login', methods=['POST'])
def login():
    print("Raw form data received:", request.form)

    username = request.form.get('login_username')
    password = request.form.get('login_password')

    print(f"Username from form: {username}")
    print(f"Password from form: {password}")

    user = User.query.filter(User.username.ilike(username.strip())).first()

    if user:
        print(f"User found: {user.username}")
        print(f"Stored password hash: {user.password}")
        
        # Check if the password matches the hash
        if check_password_hash(user.password, password):
            login_user(user)
            print(f"Stored hash: {user.password}")  # This prints the hashed password
            print(f"Password match: True")
            return jsonify({
                "message": "Login successful",
                "role": user.role,
                "user_id": user.id,
                "redirect_url": f"/me_page/{user.id}" if user.role == 'vendor' else "/products"
            }), 200
        else:
            print("Password match: False")
            return jsonify({"message": "Login failed"}), 401

    print("Login failed: invalid username or password")
    return jsonify({"message": "Login failed"}), 401

     
@app.route('/logout')
def logout():
     session.clear()  
     return redirect(url_for(''))  
    
@app.route('/')
def home():
     premium_listings = [
         {
             'img_url':'https://tse3.mm.bing.net/th?id=OIP.DDKS6ur8HQMKGxEn96pWkgHaHa&w=200&h=200&c=7',
             'title': 'Extra Large Chocolate Easter Eggs - Special Offer',
             'caption': 'Easter is around the corner!!! Place your orders for delicious chocolate-flavored Easter eggs.'
         },
         {
             'img_url': "https://images.pexels.com/photos/1006195/pexels-photo-1006195.png?auto=compress&cs=tinysrgb&w=600",  
             'title': 'Fulani Goddess Braids + Hair Dye',
             'caption': 'Check out the latest hair!! Slay this summer holiday with goddess braids of any color with matching hair.'
         },
         {
             'img_url': "https://tse4.mm.bing.net/th?id=OIP.p19rwbu1CDLxZeTnuidy6AHaE8&w=200&h=133&c=7",
             'title': 'Authentic Cameroonian Jollof Rice',
             'caption': 'Spice up your meals with our delicious home-cooked Jollof rice. Order now for a taste of Cameroon!'
         },
         {
             'img_url': "https://tse2.mm.bing.net/th?id=OIP.f5nS3I2XOHkLRsLjuBWFkgHaHa&w=200&h=200&c=7",
             'title': 'Handmade Leather Shoes',
             'caption': 'Step in style with premium handmade leather shoes crafted by skilled artisans.'
         },
         {
             'img_url': "https://tse4.mm.bing.net/th?id=OIP.2DhzlGU2XYwW5NINXx1geQHaET&w=275&h=275&c=7",
             'title': 'Luxury Spa & Massage Booking',
             'caption': 'Relax and unwind with our premium spa and massage services. Book an appointment today!'
         },
         {
             'img_url': "https://tse1.mm.bing.net/th?id=OIP.C49ryN94DvADetaGYDpNBwHaHa&w=200&h=200&c=7",
             'title': 'Home & Office Cleaning Services',
             'caption': 'Need a sparkling clean home or office? Book our professional cleaning services now!'
         }
     ]
 
     return render_template('index.html', premium_listings=premium_listings)
 
 
categories_data = {
     "Arts and Artifacts": {
         "title": "Arts and Artifacts",
         "listings": [
             {"title": "Ancient African Sculpture", 
              "img_url": "https://tse4.mm.bing.net/th?id=OIP.qxKChnJjLZR7-iO6QdkKXwHaLG&w=474&h=474&c=7",
              "description": "A beautifully crafted African sculpture from the 18th century."
              },
             {"title": "Handmade Pottery", 
              "img_url": "https://tse1.mm.bing.net/th?id=OIP.2JhOhWk8jIHqzLMNS30j2gHaGU&w=404&h=404&c=7",
              "description": "Traditional pottery made by skilled artisans."
              },
             {"title": "Tribal Mask Collection",
              "img_url": "https://tse1.mm.bing.net/th?id=OIP.hheWUvWrHyG6vs_ZZA01LwHaL2&w=474&h=474&c=7", 
              "description": "A stunning collection of rare tribal masks."
              }
         ]
     },
     "Beauty": {
         "title": "Beauty & Self Care Services",
         "listings": [
             {"title": "Luxury Spa Treatment",
              "img_url": "https://tse4.mm.bing.net/th?id=OIP.2DhzlGU2XYwW5NINXx1geQHaET&w=275&h=275&c=7", 
              "description": "Relax with our premium spa treatment packages."
              },
             {"title": "Get fresh braids with Ryan's Salon",
              "img_url": "https://images.pexels.com/photos/1661837/pexels-photo-1661837.jpeg?auto=compress&cs=tinysrgb&w=600",
              "description": "Natural and organic skincare products for glowing skin."
              },
             {"title": "Professional Makeup Services",
              "img_url": "https://tse4.mm.bing.net/th?id=OIP.qiwYBi5WREpVzwaXPNfm-QHaLG&w=200&h=300&c=7", 
              "description": "Book a makeup artist for any special occasion."}
         ]
     },
     "Food": {
         "title": "Food Reservation Services",
         "listings": [
             {"title": "Famous-Yaounde",
              "img_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrYy7OuGPKe-5sXZM3AHmdhNse9zoTUUWlXgbt8QVItMQCINzoRxTuduc&usqp=CAE&s", 
              "description": "Reserve a table at top-rated Famous restaurant in Yaounde-Bastos."
              },
             {"title": "Home-Delivered Ndole",
              "img_url": "https://tse4.mm.bing.net/th?id=OIP.sRJuZ7woAwoHp_DjRNg5lQHaEg&w=200&h=122&c=7",
              "description": "Get chef-prepared gourmet meals delivered to your doorstep."
              },
             {"title": "Cakes with Christy",
              "img_url": "https://tse1.mm.bing.net/th?id=OIP.Q_EYcRL-o_WwEkXrDgkq2QHaId&w=200&h=228&c=7",
              "description": "Check out our latest cake design! Order up"
              }
         ]
     }
 }
 
@app.route('/category/<category_name>')
def category_page(category_name):
    category = categories_data.get(category_name) 
 
    return render_template('category.html', category=category)
 
if __name__=="_main_":
     app.run(debug=True)