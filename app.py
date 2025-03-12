from flask import Flask, render_template

app = Flask(__name__)
if __name__=="_main_":
    app.run(debug=True)
    
@app.route('/')
def home():
    premium_listings = [
        {
            'src':'',
            'title': 'Extra Large Chocolate Easter Eggs - Special Offer',
            'caption': 'Easter is around the corner!!! Place your orders for delicious chocolate-flavored Easter eggs.'
        },
        {
            'src': "https://example.com/braids.jpg",  
            'title': 'Fulani Goddess Braids + Hair Dye',
            'caption': 'Check out the latest hair!! Slay this summer holiday with goddess braids of any color with matching hair.'
        },
        {
            'src': "https://example.com/jollof_rice.jpg",
            'title': 'Authentic Cameroonian Jollof Rice',
            'caption': 'Spice up your meals with our delicious home-cooked Jollof rice. Order now for a taste of Cameroon!'
        },
        {
            'src': "https://example.com/shoes.jpg",
            'title': 'Handmade Leather Shoes',
            'caption': 'Step in style with premium handmade leather shoes crafted by skilled artisans.'
        },
        {
            'src': "https://example.com/massage.jpg",
            'title': 'Luxury Spa & Massage Booking',
            'caption': 'Relax and unwind with our premium spa and massage services. Book an appointment today!'
        },
        {
            'src': "https://example.com/cleaning.jpg",
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

@app.route('/about')
def about_page():
    return render_template('about.html')
