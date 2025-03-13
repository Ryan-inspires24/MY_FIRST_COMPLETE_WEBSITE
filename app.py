from flask import Flask, render_template

app = Flask(__name__)
if __name__=="_main_":
    app.run(debug=True)
    
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


@app.route('/vendors')
def vendors_page():
    return render_template('vendors.html')

@app.route('/products')
def products_page():
    return render_template('products.html')

@app.route('/about.html')
def about_page():
    return render_template('about.html')

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



