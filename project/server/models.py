# project/server/models.py


from flask import current_app
from enum import Enum
from datetime import datetime

from project.server import db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode("utf-8")
        self.registered_on = datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User {0}>".format(self.email)

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    permalink = db.Column(db.String(255), nullable=False)
    date_created_gmt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)

    def __init__(self, name, permalink, description, price, weight):
        self.name = name
        self.permalink = permalink
        self.description = description
        self.price = price
        self.weight = weight

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<Product {0}>".format(self.name)

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))

    product = db.relationship("Product")

    def total(self):
        return self.product.price * self.quantity

class Order(db.Model):

    __tablename__ = "orders"

    class STATUS(Enum):
        PENDING = 'pending'
        COMPLETED = 'completed'
        CANCELLED = 'cancelled'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(255), nullable=False, unique=True)
    status = db.Column(db.Enum(STATUS), nullable=False, default=STATUS.PENDING)
    date_created_gmt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modification_date_gmt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    order_items = db.relationship("OrderItem")

    def get_id(self):
        return self.id

    def total(self):
        return sum(oi.total() for oi in self.order_items)

    def get_status(self):
        return self.status;

    def __repr__(self):
        return "<Order {0}>".format(self.number)