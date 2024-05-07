from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Assuming you have a models.py file with SQLAlchemy ORM classes for Customer and Product
from models import Customer, Product, Category, Order, OrderItem
from config import sql_db, sql_host, sql_password, sql_username, company_name


app = Flask(__name__)
# Replace with a secret key for session management
app.secret_key = 'your_secret_key'


engine = create_engine(
    f'mysql://{sql_username}:{sql_password}@{sql_host}/{sql_db}')
# engine = create_engine('mysql://username:password@localhost/mydb')

# Function to create a session
Session = sessionmaker(bind=engine)


@app.context_processor
def inject_orders_count():
    db_session = Session()

    # Retrieve all products from the database
    products = db_session.query(Product).all()
    order_id = session.get('order_id')
    customer_id = session.get('customer_id')
    user_logged_in = False
    user_detail = None
    if customer_id:
        user_logged_in = True
        user_detail = db_session.query(Customer).filter_by(
            id=customer_id).first()
    orders_count = 0
    if order_id:
        orders_count = len(db_session.query(OrderItem, Product.name, Product.price).join(
            Product).filter(OrderItem.order_id == order_id and Order.customer_id == customer_id).all())
    categories = dict()
    db_catagories = db_session.query(Category).all()
    for cat in db_catagories:
        categories[cat.id] = cat.name
    db_session.close()
    return dict(orders_count=orders_count, user_logged_in=user_logged_in, user_detail=user_detail, categories=categories, company_name=company_name)


def redirect_back():
    # Check if 'next' URL is present in the query parameters
    next_url = request.args.get('next')
    if next_url:
        return redirect(next_url)
    else:
        # Default redirect if 'next' URL is not present
        return redirect(url_for('home'))


@app.route('/')
def home():
    # Create a session
    db_session = Session()

    # Retrieve all products from the database
    products = db_session.query(Product).all()
    # order_id = session.get('order_id')
    # customer_id = session.get('customer_id')
    # orders_count = 0
    # if order_id:
    #     orders_count = len(db_session.query(OrderItem, Product.name, Product.price).join(
    #         Product).filter(OrderItem.order_id == order_id and Order.customer_id == customer_id).all())
    #     print(orders_count)

    # Close the session
    db_session.close()

    # Pass the products to the template and render home.html
    return render_template('home.html', products=products)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Get form data
        firstname = request.form['firstname']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']

        # Create a new customer instance
        new_customer = Customer(
            firstname=firstname, last_name=last_name, email=email, phone_number=phone_number, password=password)

        # Create a session
        db_session = Session()

        # Add the new customer to the database
        db_session.add(new_customer)
        db_session.commit()

        # Close the session
        db_session.close()

        # Redirect to the home page after sign up
        return redirect(url_for('home'))
    else:
        return render_template('sign_up.html')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Create a session
        db_session = Session()

        # Query the database for the customer with the provided email
        customer = db_session.query(Customer).filter_by(email=email).first()

        # Check if the customer exists and the password is correct
        if customer and customer.password == password:
            # Log in the customer by storing their ID in the session
            session['customer_id'] = customer.id
            db_session.close()
            # Redirect to the home page after sign in
            # return redirect(url_for('home'))
            return redirect_back()
        else:
            db_session.close()
            return 'Invalid email or password'
    else:
        return render_template('sign_in.html')


@app.route('/log_out')
def log_out():
    # Clear the customer ID from the session
    session.pop('customer_id', None)
    session.pop('order_id', None)
    # Redirect to the home page after log out
    return redirect(url_for('home'))


@app.route('/product', methods=['POST'])
def create_product():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']
        categorie_id = request.form['categorie_id']
        item_photo = request.form['item_photo'] if 'item_photo' in request.form else 'default.png'

        # Create a new product instance
        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            categorie_id=categorie_id,
            item_photo=item_photo
        )

        # Create a session
        db_session = Session()

        # Add the new product to the database
        db_session.add(new_product)
        db_session.commit()

        # Close the session
        db_session.close()

        # Redirect to the home page after product creation
        return redirect(url_for('home'))


@app.route('/product', methods=['GET'])
def new_product():
    db_session = Session()

    # Retrieve all products from the database
    catagories = db_session.query(Category).all()
    print("hey", catagories)
    # Close the session
    db_session.close()
    return render_template('new_product.html', catagories=catagories)


@app.route('/product/<int:product_id>', methods=['GET'])
def show_product(product_id):
    # Create a session
    db_session = Session()

    # Query the database for the product with the provided ID
    product = db_session.query(Product).filter_by(id=product_id).first()

    # Close the session
    db_session.close()

    # Render the template with the product data
    return render_template('show_product.html', product=product)


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    # Create a session
    db_session = Session()

    # Query the database for the product with the provided ID
    product = db_session.query(Product).filter_by(id=product_id).first()

    if product:
        # Delete the product
        db_session.delete(product)
        db_session.commit()
        result = {'message': 'Product deleted successfully'}
    else:
        result = {'error': 'Product not found'}

    # Close the session
    db_session.close()

    # Return JSON response
    return jsonify(result)


@app.route('/products')
def show_products():
    db_session = Session()

    products = db_session.query(Product).all()

    db_session.close()

    # Pass the products to the template and render home.html
    return render_template('show_products.html', products=products)


@app.route('/category', methods=['POST'])
def create_category():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']

        # Create a new category instance
        new_category = Category(name=name)

        # Create a session
        db_session = Session()

        # Add the new category to the database
        db_session.add(new_category)
        db_session.commit()

        # Close the session
        db_session.close()

        # Redirect to the home page after category creation
        return redirect(url_for('home'))


@app.route('/category', methods=['GET'])
def new_category():
    return render_template('new_category.html')


@app.route('/categories')
def show_categories():
    # Create a session
    db_session = Session()

    # Query the database for all categories
    categories = db_session.query(Category).all()

    # Close the session
    db_session.close()

    # Render the template with the categories data
    return render_template('show_categories.html', categories=categories)


@app.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    # Create a session
    db_session = Session()

    # Query the database for the category with the provided ID
    category = db_session.query(Category).filter_by(id=category_id).first()

    if category:
        # Delete the category
        db_session.delete(category)
        db_session.commit()
        result = {'message': 'Category deleted successfully'}
    else:
        result = {'error': 'Category not found'}

    # Close the session
    db_session.close()

    # Return JSON response
    return jsonify(result)


@app.route('/order_item', methods=['POST'])
def create_order_item():
    if request.method == 'POST':
        # Get form data
        product_id = request.form['product_id']
        quantity = request.form['quantity']

        # Get the customer ID from the session
        customer_id = session.get('customer_id')
        if not customer_id:
            # Handle the case when the user is not logged in
            return redirect(url_for('sign_in', next=request.url))

        # Get the order ID from the session or create a new order if not found
        order_id = session.get('order_id')
        if not order_id:
            # Create a new order
            new_order = Order(total_amount=0, customer_id=customer_id)
            db_session = Session()
            db_session.add(new_order)
            db_session.commit()
            order_id = new_order.id
            session['order_id'] = order_id
            db_session.close()

        # Create a new order item instance

        # Create a session
        db_session = Session()
        product = db_session.query(Product).get(product_id)

        new_order_item = OrderItem(
            order_id=order_id, product_id=product_id, quantity=quantity, unit_price=product.price)
        # Add the new order item to the database
        db_session.add(new_order_item)

        # Update total_amount in the order table
        order = db_session.query(Order).get(order_id)
        order.total_amount += 1
        db_session.commit()

        # Close the session
        db_session.close()

        # Redirect to the home page or any other page you prefer
        return redirect(url_for('home'))


@app.route('/orders')
def show_orders():
    order_id = session.get('order_id')
    customer_id = session.get('customer_id')
    print("print order", order_id)
    if not order_id:
        # No order ID found in the session, render an empty orders page
        return render_template('show_orders.html', order_items=[])
    if not customer_id:
        return redirect(url_for('sign_in', next=request.url))

    # db_session = Session()

    # # Query the database for all order items with the current order ID
    # order_items = db_session.query(
    #     OrderItem).filter_by(order_id=order_id).all()

    # # Close the session
    # db_session.close()

    # Create a session
    db_session = Session()

    # Query the database to fetch order items and associated product names
    query = db_session.query(OrderItem, Product.name, Product.price).join(
        Product).filter(OrderItem.order_id == order_id and Order.customer_id == customer_id)
    order_items_with_names = query.all()

    # Close the session
    db_session.close()

    return render_template('show_orders.html', order_items=order_items_with_names)


@app.route('/order_item/<int:order_item_id>', methods=['DELETE'])
def delete_order_item(order_item_id):
    db_session = Session()

    # Query the database for the order item with the provided ID
    order_item = db_session.query(OrderItem).get(order_item_id)
    if not order_item:
        db_session.close()
        return jsonify({'error': 'Order item not found'}), 404

    # Get the order ID before deleting the order item
    order_id = order_item.order_id

    # Delete the order item
    db_session.delete(order_item)

    # Update total_amount in the order table
    order = db_session.query(Order).get(order_id)
    order.total_amount -= 1
    db_session.commit()

    # Close the session
    db_session.close()

    return jsonify({'message': 'Order item deleted successfully'}), 200


@app.route('/order', methods=['DELETE'])
def delete_order():
    order_id = session.get('order_id')
    if not order_id:
        return jsonify({'error': 'No order found in session'}), 404

    db_session = Session()

    # Query the database for the order with the current order ID
    order = db_session.query(Order).get(order_id)
    if not order:
        db_session.close()
        return jsonify({'error': 'Order not found'}), 404

    # Delete the order
    db_session.delete(order)
    db_session.commit()

    # Remove the order ID from the session
    session.pop('order_id')

    # Close the session
    db_session.close()

    return jsonify({'message': 'Order deleted successfully'}), 200


@app.route('/order_histories')
def all_orders():

    # Create a session
    db_session = Session()

    # Query the database to fetch all orders for the current customer
    orders = db_session.query(Order).all()
    for new in orders:
        for item in new.items:
            item.product
    # Close the session
    db_session.close()

    # Render the template with the orders data
    return render_template('all_orders.html', orders=orders)


@app.route('/order_history')
def order_history():
    # Get the customer ID from the session
    customer_id = session.get('customer_id')
    if not customer_id:
        # Handle the case when the customer ID is not found in the session
        # Redirect to the sign-in page or show an error message
        return redirect(url_for('sign_in', next=request.url))

    # Create a session
    db_session = Session()
    orders = db_session.query(Order).filter(
        Order.customer_id == customer_id).all()
    for new in orders:
        for item in new.items:
            item.product

            # Close the session
    db_session.close()

    # Render the template with the orders data
    return render_template('show_order_history.html', orders=orders)


@app.route('/buy', methods=['POST'])
def buy():
    # Get the order ID from the session
    order_id = session.get('order_id')
    if not order_id:
        # Handle the case when the order ID is not found in the session
        # Redirect to an appropriate page or show an error message
        return redirect(url_for('home'))

    # Create a session
    db_session = Session()

    # Query the database to fetch the order
    order = db_session.query(Order).filter_by(id=order_id).first()
    print(order)
    if order:
        # Update the total_amount to -1 to indicate the order is ordered and delivered
        order.total_amount = -1
        db_session.commit()

        # Clear the order ID from the session
        session.pop('order_id', None)

        # Close the session
        db_session.close()

        # Redirect to the home page or any other page you prefer
        return redirect(url_for('home'))
    else:
        # Handle the case when the order is not found
        # Redirect to an appropriate page or show an error message
        db_session.close()
        return redirect(url_for('home'))  # Redirect to home for now


@app.route('/admin')
def admin_page():
    return render_template('admin_page.html')


if __name__ == '__main__':
    app.run(debug=True)
