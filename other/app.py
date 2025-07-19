from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import razorpay
import requests
import json
from datetime import datetime
import calendar
import random

app = Flask(__name__)
app.secret_key = "secret"

# Razorpay API credentials
razorpay_client = razorpay.Client(auth=("rzp_test_maJx76beM9pPzk", "nMt5oByuD7ebNWlByhnuMudI"))

# Dummy data for authentication
users = {"user": "user123"}
admin = {"admin": "admin123"}
scrap_processors = {"processor": "processor123"}
buyers = {"buyer": "buyer123"}

# Scrap details storage
scrap_data = []

# Initialize default scrap quantities and prices
processed_scrap = [{
    "steel": 1000,  # 1000 kg of steel
    "aluminium": 800,  # 800 kg of aluminium
    "copper": 100  # 100 kg of copper
}]

cost_per_kg = {
    "steel": 12,  # ₹12 per kg
    "aluminium": 10,  # ₹10 per kg
    "copper": 8  # ₹8 per kg
}

# Monthly revenue tracking
monthly_revenue = {}

# New registrations tracking
new_registrations = []

# Add a new dictionary to store payment history
payment_history = []

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/join')
def join():
    return render_template("join.html")

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Check if username already exists in any role
        if (username in users or username in admin or 
            username in scrap_processors or username in buyers):
            flash('Username already exists! Please choose a different username.', 'error')
            return redirect(url_for('register'))
        
        # Store user data based on role
        if role == 'user':
            users[username] = password
            # Add to new registrations
            new_registrations.append({
                "username": username,
                "role": "User",
                "registration_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active"
            })
            flash('You have successfully registered as a User! Please login.', 'success')
            return redirect(url_for('login'))
        elif role == 'scrap_processor':
            scrap_processors[username] = password
            # Add to new registrations
            new_registrations.append({
                "username": username,
                "role": "Processor",
                "registration_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active"
            })
            flash('You have successfully registered as a Scrap Processor! Please login.', 'success')
            return redirect(url_for('login'))
        elif role == 'buyer':
            buyers[username] = password
            # Add to new registrations
            new_registrations.append({
                "username": username,
                "role": "Buyer",
                "registration_date": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active"
            })
            flash('You have successfully registered as a Buyer! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid role selected!', 'error')
            return redirect(url_for('register'))
            
    return render_template("login.html")

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
            "status": "pending"  # Add default status for new submissions
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
    
    # Only show approved scraps
    approved_scraps = [scrap for scrap in scrap_data if scrap.get('status') == "approved"]
    
    # Calculate total processed weight
    total_weight = sum(
        float(item.get('steel', 0)) + 
        float(item.get('aluminium', 0)) + 
        float(item.get('copper', 0)) 
        for item in processed_scrap
    )
    
    # Get recent activity (last 5 entries)
    recent_activity = processed_scrap[:5]
    
    if request.method == 'POST':
        # Get form data
        steel = float(request.form['steel'])
        aluminium = float(request.form['aluminium'])
        copper = float(request.form['copper'])
        
        # Calculate total weight
        total_new_weight = steel + aluminium + copper
        
        # Create a new entry instead of replacing the first one
        new_processed_scrap = {
            "steel": steel,
            "aluminium": aluminium,
            "copper": copper,
            "date": "Today",
            "processor_name": session.get('processor', 'Processor 1'),
            "status": "completed"
        }
        
        # Add the new entry to the beginning of the list
        processed_scrap.insert(0, new_processed_scrap)
        
        # Keep only the last 10 entries to avoid the list growing too large
        if len(processed_scrap) > 10:
            processed_scrap.pop()
            
        # Create a detailed success message
        success_message = f'Success! You have processed {total_new_weight:.1f} kg of scrap (Steel: {steel:.1f} kg, Aluminium: {aluminium:.1f} kg, Copper: {copper:.1f} kg).'
        
        # Redirect with success message in URL parameters
        return redirect(url_for('processor_dashboard', success=True, message=success_message))
    
    return render_template("processor_dashboard.html", 
                         scraps=approved_scraps,
                         total_weight=total_weight,
                         recent_activity=recent_activity,
                         last_update_time=processed_scrap[0].get('date', 'Today') if processed_scrap else 'Today')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    # Handle price setting form submission
    if request.method == 'POST':
        # Get the form data
        steel_cost = float(request.form.get('steel_cost', 0))
        aluminium_cost = float(request.form.get('aluminium_cost', 0))
        copper_cost = float(request.form.get('copper_cost', 0))
        
        # Update the cost_per_kg dictionary
        cost_per_kg.update({
            'steel': steel_cost,
            'aluminium': aluminium_cost,
            'copper': copper_cost
        })
        
        # Flash a success message
        flash('Prices updated successfully!', 'success')
        
        # Redirect to prevent form resubmission
        return redirect(url_for('admin_dashboard'))
    
    # Calculate total revenue
    total_revenue = sum(monthly_revenue.values())
    
    # Pass all necessary data to the template
    return render_template('admin_dashboard.html',
                         scraps=scrap_data,
                         processed_scrap=processed_scrap,
                         new_registrations=new_registrations,
                         total_revenue=total_revenue,
                         cost_per_kg=cost_per_kg)

@app.route('/buyer_dashboard')
def buyer_dashboard():
    if 'buyer' not in session:
        return redirect(url_for('login'))
    
    try:
        # Initialize default values
        processed_scrap = [{"steel": 0, "aluminium": 0, "copper": 0}]
        cost_per_kg = {"steel": 12, "aluminium": 10, "copper": 8}
        
        # Get transactions for the current buyer
        buyer_transactions = []
        if payment_history:
            buyer_transactions = [t for t in payment_history if t.get('buyer') == session.get('buyer')]
        
        # Format transactions with status classes and icons
        formatted_transactions = []
        for transaction in buyer_transactions:
            status_class = 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
            status_icon = 'fa-check-circle'
            
            formatted_transaction = {
                'id': transaction.get('transaction_id', 'N/A'),
                'date': transaction.get('payment_date', 'N/A'),
                'scrap_type': transaction.get('scrap_type', 'N/A'),
                'weight': transaction.get('weight', '0'),
                'amount': transaction.get('amount', '0'),
                'status': 'Completed',
                'status_class': status_class,
                'status_icon': status_icon
            }
            formatted_transactions.append(formatted_transaction)
        
        # Get the latest processed scrap data
        latest_processed_scrap = processed_scrap[0] if processed_scrap else {"steel": 0, "aluminium": 0, "copper": 0}
        
        # Add current datetime for the template
        current_time = datetime.now().strftime('%H:%M:%S')
        
        return render_template("buyer_dashboard.html", 
                            processed_scrap=processed_scrap,
                            latest_processed_scrap=latest_processed_scrap,
                            cost_per_kg=cost_per_kg,
                            transactions=formatted_transactions,
                            current_time=current_time)
    
    except Exception as e:
        print(f"Error in buyer_dashboard: {str(e)}")
        flash("An error occurred while loading the dashboard. Please try again.", "error")
        return redirect(url_for('login'))

@app.route('/buy_now', methods=['POST'])
def buy_now():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    scrap_type = request.form.get('scrap_type')
    weight = float(request.form.get('weight', 0))
    
    # Check if enough quantity is available
    available_quantity = 0
    for item in processed_scrap:
        if item.get('type') == scrap_type:
            available_quantity = float(item.get('quantity', 0))
            break
    
    if available_quantity < weight:
        flash('Not enough quantity available!', 'error')
        return redirect(url_for('buyer_dashboard'))
    
    # Calculate price based on weight and scrap type
    price_per_kg = 0
    if scrap_type == 'steel':
        price_per_kg = 50  # Example price
    elif scrap_type == 'aluminium':
        price_per_kg = 100  # Example price
    elif scrap_type == 'copper':
        price_per_kg = 200  # Example price
    
    total_price = weight * price_per_kg

    # Store purchase details in session
    if 'cart' not in session:
        session['cart'] = []

    # Add to cart
    cart_item = {
        'type': scrap_type,
        'weight': weight,
        'price': total_price
    }
    session['cart'].append(cart_item)
    
    # Calculate grand total
    grand_total = sum(item.get('price', 0) for item in session['cart'])
    session['grand_total'] = grand_total
    
    # Redirect to payment page
    return render_template('payment.html', grand_total=grand_total)

@app.route('/payment_page')
def payment_page():
    return render_template("payment_page.html")

@app.route('/bill')
def bill():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    grand_total = session.get('grand_total', 0)
    
    # Decrease scrap quantities for each item in the cart
    for item in cart_items:
        scrap_type = item.get('type')
        weight = float(item.get('weight', 0))
        
        # Find the corresponding processed scrap item and decrease quantity
        for processed_item in processed_scrap:
            if processed_item.get('type') == scrap_type:
                current_quantity = float(processed_item.get('quantity', 0))
                if current_quantity >= weight:
                    processed_item['quantity'] = current_quantity - weight
                else:
                    print(f"Warning: Attempted to decrease {scrap_type} below available quantity")
    
    # Update monthly revenue
    current_month = datetime.now().strftime("%b")
    monthly_revenue[current_month] = monthly_revenue.get(current_month, 0) + grand_total
    
    # Log the revenue update
    print(f"Revenue update (bill): Added {grand_total} to {current_month}. New total: {monthly_revenue[current_month]}")
    
    # Add payment to history
    payment_record = {
        'buyer': session.get('username', 'Unknown'),
        'scrap_type': ', '.join([item.get('type') for item in cart_items]),
        'weight': sum(float(item.get('weight', 0)) for item in cart_items),
        'amount': grand_total,
        'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'Completed'
    }
    payment_history.append(payment_record)
    
    # Clear the cart session
    session.pop('cart', None)
    session.pop('grand_total', None)
    
    return render_template('bill.html', cart_items=cart_items, grand_total=grand_total)

@app.route('/payment_success', methods=['POST'])
def payment_success():
    try:
        # Get payment details from form data
        razorpay_payment_id = request.form.get('razorpay_payment_id')
        razorpay_order_id = request.form.get('razorpay_order_id')
        razorpay_signature = request.form.get('razorpay_signature')
        cart_items = json.loads(request.form.get('cart_items', '[]'))
        
        # Verify payment with Razorpay
        params_dict = {
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature
        }

        # Verify the payment signature
        razorpay_client.utility.verify_payment_signature(params_dict)

        # Update scrap quantities
        for item in cart_items:
            scrap_type = item.get('type')
            weight = float(item.get('weight', 0))
            
            # Update the processed scrap quantities
            if processed_scrap and len(processed_scrap) > 0:
                latest_scrap = processed_scrap[0]
                if scrap_type in latest_scrap:
                    latest_scrap[scrap_type] = max(0, latest_scrap[scrap_type] - weight)
        
        # Create transaction record
        transaction = {
            'transaction_id': razorpay_payment_id,
            'buyer': session.get('buyer'),
            'scrap_type': ', '.join([item.get('name') for item in cart_items]),
            'weight': sum(float(item.get('weight', 0)) for item in cart_items),
            'amount': sum(float(item.get('price', 0)) for item in cart_items),
            'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Completed'
        }
        
        # Add to payment history
        payment_history.append(transaction)
        
        # Update monthly revenue
        current_month = datetime.now().strftime("%b")
        monthly_revenue[current_month] = monthly_revenue.get(current_month, 0) + transaction['amount']
        
        return jsonify({
            'status': 'success',
            'message': 'Payment verified and processed successfully',
            'transaction_id': razorpay_payment_id,
            'amount': transaction['amount']
        })
        
    except Exception as e:
        print(f"Error in payment_success: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

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

@app.route('/approve_scrap/<scrap_name>', methods=['POST'])
def approve_scrap(scrap_name):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    # Find the scrap item by name and mark it as approved
    for scrap in scrap_data:
        if scrap['name'] == scrap_name:
            scrap['status'] = "approved"
            flash(f'Scrap "{scrap_name}" has been approved successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    flash(f'Scrap "{scrap_name}" not found!', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_scrap/<scrap_name>', methods=['POST'])
def reject_scrap(scrap_name):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    # Find the scrap item by name and mark it as rejected
    for scrap in scrap_data:
        if scrap['name'] == scrap_name:
            scrap['status'] = "rejected"
            flash(f'Scrap "{scrap_name}" has been rejected.', 'error')
            return redirect(url_for('admin_dashboard'))
    
    flash(f'Scrap "{scrap_name}" not found!', 'error')
    return redirect(url_for('admin_dashboard'))

# Add API endpoint for refreshing processed scrap data
@app.route('/api/processed_scrap')
def get_processed_scrap():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Return the processed scrap data
    return jsonify(processed_scrap)

# Add API endpoint for user scrap data
@app.route('/api/user_scrap_data')
def api_user_scrap_data():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify(scrap_data)

# Add API endpoint for monthly revenue data
@app.route('/api/monthly_revenue')
def get_monthly_revenue():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get the current month
        current_month = datetime.now().strftime("%b")
        
        # Ensure the current month exists in the dictionary
        if current_month not in monthly_revenue:
            monthly_revenue[current_month] = 0
        
        # Log the revenue data for debugging
        print(f"Monthly revenue data: {monthly_revenue}")
        
        return jsonify(monthly_revenue)
    except Exception as e:
        print(f"Error in monthly revenue API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Add API endpoint to check for revenue updates
@app.route('/api/check_revenue_updates')
def check_revenue_updates():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get the current month
        current_month = datetime.now().strftime("%b")
        
        # Ensure the current month exists in the dictionary
        if current_month not in monthly_revenue:
            monthly_revenue[current_month] = 0
        
        # Calculate total revenue
        total_revenue = sum(monthly_revenue.values())
        
        # Log the update check for debugging
        print(f"Revenue update check - Current month: {current_month}, Revenue: {monthly_revenue[current_month]}, Total: {total_revenue}")
        
        return jsonify({
            'current_month_revenue': monthly_revenue[current_month],
            'total_revenue': total_revenue
        })
    except Exception as e:
        print(f"Error in revenue update check API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/scrap_history')
def get_scrap_history():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Return the scrap history data
    return jsonify(scrap_data)

@app.route('/api/buyer_scrap_data')
def get_buyer_scrap_data():
    try:
        return jsonify({
            "processed_scrap": processed_scrap[0] if processed_scrap else {"steel": 0, "aluminium": 0, "copper": 0},
            "cost_per_kg": cost_per_kg
        })
    except Exception as e:
        print(f"Error in get_buyer_scrap_data: {str(e)}")
        return jsonify({
            "error": "Failed to fetch scrap data"
        }), 500

@app.route('/api/payment_history')
def get_payment_history():
    if 'admin' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify(payment_history)

@app.route('/api/transactions')
def get_transactions():
    if 'buyer' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get transactions for the current buyer
    buyer_transactions = [t for t in payment_history if t.get('buyer') == session.get('buyer')]
    
    # Format transactions with status classes and icons
    formatted_transactions = []
    for transaction in buyer_transactions:
        status_class = 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
        status_icon = 'fa-check-circle'
        
        formatted_transaction = {
            'id': transaction.get('transaction_id', 'N/A'),
            'date': transaction.get('payment_date', 'N/A'),
            'scrap_type': transaction.get('scrap_type', 'N/A'),
            'weight': transaction.get('weight', '0'),
            'amount': transaction.get('amount', '0'),
            'status': 'Completed',
            'status_class': status_class,
            'status_icon': status_icon
        }
        formatted_transactions.append(formatted_transaction)
    
    return jsonify(formatted_transactions)

@app.route('/api/transaction/<transaction_id>')
def get_transaction_details(transaction_id):
    if 'buyer' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Find the transaction
    transaction = next((t for t in payment_history if t.get('transaction_id') == transaction_id), None)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Format transaction details
    formatted_transaction = {
        'id': transaction.get('transaction_id', 'N/A'),
        'date': transaction.get('payment_date', 'N/A'),
        'scrap_type': transaction.get('scrap_type', 'N/A'),
        'weight': transaction.get('weight', '0'),
        'amount': transaction.get('amount', '0'),
        'status': 'Completed'
    }
    
    return jsonify(formatted_transaction)

if __name__ == '__main__':
    app.run(debug=True)
