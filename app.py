from flask import Flask, render_template

app = Flask(__name__)
if __name__=="_main_":
    app.run(debug=True)
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/vendors')
def vendors_page():
    return render_template('vendors.html')

@app.route('/products')
def products_page():
    return render_template('products.html')

@app.route('/about')
def about_page():
    return render_template('about.html')
