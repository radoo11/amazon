# project/server/tests/test_order.py

import unittest
import json

from base import BaseTestCase, AuthorizedTestCase
from project.server.models import Product, Order, OrderItem
from project.server import db

class TestOrderBlueprint(AuthorizedTestCase):

    headers = {'content-type': 'application/json'}

    test_product1_id = 1
    test_productName = 'TV'
    test_productLink = 'amazon.com/TV/123'
    test_productDescription = 'TV Toshiba'
    test_productPrice = 800
    test_productWeight = 100

    test_product2_id = 2
    test_product2Name = 'VHS'
    test_product2Link = 'amazon.com/VHS/123'
    test_product2Description = 'VHS Test'
    test_product2Price = 300
    test_product2Weight = 30

    test_user_id = 1
    test_order_number = 'ZAM/XXXXXX'
    test_order_id = 1
    test_product_quantity = 10;

    test_order_status_pending = Order.STATUS.PENDING.name
    test_order_status_cancelled = Order.STATUS.CANCELLED.name

    test_order_details = {
        'number': test_order_number,
        'order_items': [
            {
                'product_id': test_product1_id,
                'quantity': test_product_quantity
            },
            {
                'product_id': test_product2_id,
                'quantity': test_product_quantity
            }
        ]
    }

    def helper_add_products(self):
        p = Product(self.test_productName, self.test_productLink, self.test_productDescription,
                    self.test_productPrice, self.test_productWeight)
        p2 = Product(self.test_product2Name, self.test_product2Link, self.test_product2Description,
                    self.test_product2Price, self.test_product2Weight)

        db.session.add(p)
        db.session.add(p2)
        db.session.commit()

    def helper_add_order_for_user(self, order_number, user_id, order_status):
        order = Order()
        order.number = order_number
        order.user_id = user_id
        order.status = order_status
        db.session.add(order)
        db.session.commit()

    def helper_add_order_item_to_order(self, product_id, quantity, order_id):
        oi = OrderItem()
        oi.product_id = product_id
        oi.quantity = quantity
        oi.order_id = order_id
        db.session.add(oi)
        db.session.commit()

### post() order tests - creating new orders
    def test_user_create_order_without_params_return_404(self):
        with self.client:
            response = self.client.post(
                "/orders"
            )
            self.assertEqual(response.status_code, 404)

    def test_user_create_order_return_201(self):
        self.helper_add_products()
        with self.client:
            response = self.client.post(
                "/orders",
                data=json.dumps(self.test_order_details, indent=4, sort_keys=True),
                headers=self.headers
            )
            self.assertEqual(response.status_code, 201)

    def test_user_created_orders_correctly(self):
        self.helper_add_products()
        with self.client:
            response = self.client.post(
                "/orders",
                data=json.dumps(self.test_order_details, indent=4, sort_keys=True),
                headers=self.headers
            )
            user_order_result = Order.query.filter(Order.user_id == self.test_user_id).first()
            user_order_items = OrderItem.query.filter(OrderItem.order_id == user_order_result.id).all()

            self.assertEqual(user_order_result.number, self.test_order_number)
            self.assertEqual(len(user_order_items), 2)
            self.assertEqual(response.status_code, 201)