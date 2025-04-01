from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import razorpay

import requests
import json



app = Flask(__name__)
app.secret_key = "secret"


# Razorpay API credentials
razorpay_client = razorpay.Client(auth=("rzp_test_h2s4PxBwrmOiSL", "beJB0s8KqtrFC8JnRjpJsYOl"))


# Dummy data for authentication
users = {"user": "user123"}
admin = {"admin": "admin123"}
scrap_processors = {"processor": "processor123"}
buyers = {"buyer": "buyer123"}

# Scrap details storage
scrap_data = []
processed_scrap = [{"steel": 0, "aluminium": 0, "copper": 0}]
cost_per_kg = {"steel": 0, "aluminium": 0, "copper": 0}

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('user_dashboard'))
        elif username in admin and admin[username] == password:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        elif username in scrap_processors and scrap_processors[username] == password:
            session['processor'] = username
            return redirect(url_for('processor_dashboard'))
        elif username in buyers and buyers[username] == password:
            session['buyer'] = username
            return redirect(url_for('buyer_dashboard'))
        else:
            return "Invalid Credentials! Try again."
    return render_template("login.html")

@app.route('/register')
def register():
    return "Register Page"

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        scrap = {
            "name": request.form['name'],
            "condition": request.form['type'],
            "weight": request.form['weight'],
            "price": request.form['price'],
            "pickup_date": request.form['pickup_date'],
            "pickup_slot": request.form['pickup_slot'],
            "approved": False
        }
        scrap_data.append(scrap)
    return render_template("user_dashboard.html", scrap_data=scrap_data)

@app.route('/submit_scrap', methods=['POST'])
def submit_scrap():
    try:
        name = request.form['name']
        condition = request.form['condition']
        weight = request.form['weight']
        price = request.form['price']
        pickup_date = request.form['pickup_date']
        pickup_slot = request.form['pickup_slot']
        return "Scrap submitted successfully!"
    except KeyError as e:
        return f"Missing form field: {str(e)}", 400

@app.route('/processor_dashboard', methods=['GET', 'POST'])
def processor_dashboard():
    if 'processor' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        processed_scrap[0] = {
            "steel": float(request.form['steel']),
            "aluminium": float(request.form['aluminium']),
            "copper": float(request.form['copper'])
        }
    return render_template("processor_dashboard.html", scraps=scrap_data)

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        cost_per_kg.update({
            "steel": float(request.form['steel_cost']),
            "aluminium": float(request.form['aluminium_cost']),
            "copper": float(request.form['copper_cost'])
        })
    return render_template("admin_dashboard.html", scraps=scrap_data, processed_scrap=processed_scrap, cost_per_kg=cost_per_kg)

@app.route('/buyer_dashboard', methods=['GET', 'POST'])
def buyer_dashboard():
    if 'buyer' not in session:
        return redirect(url_for('login'))
    
    total_price = None
    message = ""

    if request.method == 'POST':
        scrap_type = request.form['scrap_type']
        weight = float(request.form['weight'])

        # Check if the required quantity is available
        if processed_scrap[0][scrap_type] >= weight:
            total_price = weight * cost_per_kg[scrap_type]
            
            if 'buy_now' in request.form:
                processed_scrap[0][scrap_type] -= weight  # Reduce the quantity after purchase
                return redirect(url_for('buyer_dashboard'))
        else:
            message = "Scrap not available in the requested quantity."

    # Check if any scrap is available for purchase
    available_scrap = any(item > 0 for item in processed_scrap[0].values())

    return render_template("buyer_dashboard.html", processed_scrap=processed_scrap, 
                           cost_per_kg=cost_per_kg, total_price=total_price, 
                           available_scrap=available_scrap, message=message)
@app.route('/buy_now', methods=['POST'])
def buy_now():
    scrap_type = request.form.get('scrap_type')
    weight = request.form.get('weight')

    if not scrap_type or not weight:
        return "Invalid data!", 400

    weight = float(weight)
    price = weight * cost_per_kg[scrap_type]

    # Store purchase details in session
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'scrap_type': scrap_type, 'weight': weight, 'price': price})
    session['grand_total'] = sum(item['price'] for item in session['cart'])

    # Pass the calculated grand total to the payment page
    total_amount = session['grand_total'] * 100  # Razorpay uses paise

    return render_template("payment_page.html", amount=total_amount)



@app.route('/payment_page')
def payment_page():
    return render_template("payment_page.html")

@app.route('/bill')
def bill():
    cart_items = session.get('cart', [])
    grand_total = session.get('grand_total', 0)
    
    session.pop('cart', None)  # Clear cart after billing
    session.pop('grand_total', None)
    
    return render_template('bill.html', cart_items=cart_items, grand_total=grand_total)
@app.route("/payment_success", methods=['POST'])
def payment_success():
    try:
        # Verify payment signature
        razorpay_payment_id = request.form['razorpay_payment_id']
        razorpay_order_id = request.form['razorpay_order_id']
        razorpay_signature = request.form['razorpay_signature']

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        # Signature verification
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Clear the cart after successful payment
        session.pop('cart', None)
        session.pop('grand_total', None)

        return render_template("payment_success.html")
    except razorpay.errors.SignatureVerificationError:
        return "Payment verification failed!", 400
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        amount = int(request.form['amount'])
        
        # Create Razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'order_id': order['id'],
            'amount': amount
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
