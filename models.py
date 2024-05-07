from sqlalchemy import create_engine, Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
# Create SQLAlchemy engine
# Update with your database connection details
# from dotenv import get_variables
# import os
# # Load environment variables from .env file
# load_dotenv()

# Access environment variables
# sql_username = get_variable('.env', "SQL_USERNAME")
# sql_password = get_variable('.env', "SQL_PASSWORD")
# sql_host = get_variable('.env', "SQL_HOST")
# sql_db = get_variable('.env', "SQL_DB")
sql_username = 'root'
sql_password = 'password'
sql_host = 'localhost'
sql_db = 'mydb'

engine = create_engine(
    f'mysql://{sql_username}:{sql_password}@{sql_host}/{sql_db}')

# Create base class for declarative class definitions
Base = declarative_base()

# Define Customer class


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    phone_number = Column(String(45), nullable=False)
    region = Column(String(45), default='not set')
    city = Column(String(45), default='not set')
    password = Column(String(45), nullable=False)

# Define Category class


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)

# Define Product class


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    description = Column(String(45), nullable=False)
    price = Column(DECIMAL, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    item_photo = Column(String(255), default='default.png')

    category = relationship("Category")

# Define Order class


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_date = Column(DateTime, nullable=False, default=datetime.now)
    total_amount = Column(DECIMAL, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))

    customer = relationship("Customer")

# Define OrderItem class


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    order = relationship("Order")
    product = relationship("Product")


# Create all tables in the database
Base.metadata.create_all(engine)
