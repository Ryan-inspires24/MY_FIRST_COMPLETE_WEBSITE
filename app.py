from flask import Flask, render_template, request, redirect, flash, jsonify, url_for, abort, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import requests

import os


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ryan_inspires:Asherinyuy24@localhost/caminspo_db'
app.secret_key = 'Gxo/24#9' 
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

db = SQLAlchemy(app)

class Product_categories(db.Model): 
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

class Vendors(db.Model):
    vendor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False) 
    surname = db.Column(db.String(255), nullable=False) 
    username = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)
    vendor_email = db.Column(db.String(255), nullable=False, unique=True)
    password =db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)  

    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(255), nullable=True)

    products = db.relationship('Products', back_populates='vendor', lazy=True)


class Products(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    product_pic = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.category_id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.vendor_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor = db.relationship('Vendors', back_populates='products', lazy=True)
    category = db.relationship('Product_categories', backref="products") 

# @app.route('/add_product', methods=['GET','POST'])

@app.route('/me/<int:vendor_id>')
def me_page(vendor_id):
    vendor = Vendors.query.get_or_404(vendor_id)
    return render_template('me_page.html', vendor=vendor)



@app.route('/db_setup')
def db_setup():
        db.create_all() 
        return 'CamInspo Database successfully created!'
    

@app.route('/vendors.html')
def vendors_page():
    vendors = Vendors.query.all()  
    return render_template('vendors.html', vendors=vendors)

@app.route('/products.html')
def products_page():
    products = Products.query.all()  
    return render_template("products.html", products=products)

@app.route('/product/<int:product_id>')
def product_details(product_id):
    product = Products.query.get(product_id)  
    if product:
        return render_template("product_details.html", product=product)
    return "Product not found", 404

@app.route('/vendor/<int:vendor_id>')
def vendor_profile(vendor_id):
    vendor = Vendors.query.get(vendor_id)
    if not vendor:
        abort(404) 
    return render_template("vendor_profile.html", vendor=vendor)

@app.route('/about.html')
def about_page():
    return render_template('about.html')


@app.route('/api/register', methods=['POST', 'GET'])
def register():
    # if 'profile_picture' not in request.files:
    #     return jsonify({"error": "Profile picture is required"}), 400
    if request.method =='POST':
        profile_picture = request.files['profile_picture']
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        username = request.form.get('register_username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('register_password')
        description = request.form.getlist('description')

        # if not all([first_name, surname, username, email, phone_number, password, description]):
        #     return jsonify({"error": "All fields are required!"}), 400
        
        # if Vendors.query.filter_by(vendor_email=email).first():
        #     return jsonify({"error": "Email already registered"}), 400
        
        # if Vendors.query.filter_by(username=username).first():
        #     return jsonify({"error": "Username already exists"}), 400
        
        files=[]
        for pic in profile_picture:
          files.append('inline', (pic.filename, pic.stream, pic.mimetype))  
        
        url = "https://api.mailgun.net/v3/sandbox731194d37470413e8c548a52a345d7c7.mailgun.org/messages"
        data={
            'from' : 'contactformservices@sandbox731194d37470413e8c548a52a345d7c7.mailgun.org',
                'to' : [email],
                'subject' : 'Successful Registration!',
                'text': f' Welcome {username}. ',
                'html' : f'''
                        <html>
                        <body>
                        <h2> Hi {username}! Welcome to CamInspo Market Hub.</h2>
                        <strong>Your Info</strong>
                        <ul> Username - {username} </ul>
                        <ul> Email Adress - {email} </ul>
                        <ul> Phone Number - {phone_number} </ul>

                        <p> What are you waiting for? upload images to your product informtion on your account and access over 500000 customers! </p>
                        </body>
                        </html>
                            '''
            }
        files = files
        auth = ("api", "04e7193703a33f3123f6eb1cf196e9bb-24bda9c7-1550a8f8")
        
        response = requests.post(url, auth=auth, data=data, files=files)
        print('Response Status Code: ', response.status_code)
        print(response.json())
        flash(f'{username} registered with success!', 'success')
    return render_template('base_template.html')
    


#     filename = f"{username}_{profile_picture.filename}"
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     profile_picture.save(filepath)

#     hashed_password = generate_password_hash(password)

#     new_vendor = Vendors(
#         first_name=first_name,
#         surname=surname,
#         username=username,
#         vendor_email=email,
#         phone_number=phone_number,
#         password=hashed_password,
#         description=description,
#         profile_pic=filepath  
#     )

#     db.session.add(new_vendor)
#     db.session.commit()

#     return jsonify({"message": "Registration successful!", "vendor_id": new_vendor.vendor_id}), 201
    


# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('login_username')
#     password = request.form.get('login_password')

#     user = Vendors.query.filter_by(username=username).first()

#     if user and check_password_hash(user.password, password): 
#         session['user_id'] = user.vendor_id
#         session['username'] = user.username
#         flash("login Successful", "success")
#         return redirect(url_for('me_page'))
#     else:
#         flash('Either username,password or both are incorrect.','danger')
#         return redirect(url_for('vendors_page'))
     
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
    
