# project/server/tests/test_product.py

import unittest
import json

from base import BaseTestCase
from project.server.models import Product
from project.server import db

class TestProductBlueprint(BaseTestCase):

    test_productName = 'Telewizor'
    test_productLink = 'amazon.mvp.pl/television/34'
    test_productDescription = 'Telewizor firmy Toshiba'
    test_productPrice = 1200
    test_productWeight = 80

    def helper_add_product(self):
        p = Product(self.test_productName, self.test_productLink, self.test_productDescription,
                    self.test_productPrice, self.test_productWeight)
        db.session.add(p)
        db.session.commit()

    def test_empty_product_list_return_404(self):
        with self.client:
            response = self.client.get(
                "/products"
            )
            self.assertEqual(response.status_code, 404)

    def test_product_list_with_one_element_return_200(self):
        self.helper_add_product()
        with self.client:
            response = self.client.get(
                "/products"
            )
            self.assertEqual(response.status_code, 200)

    def test_product_list_has_correct_count_when_more_than_one_product(self):
        self.helper_add_product()
        self.helper_add_product()
        self.helper_add_product()
        with self.client:
            response = self.client.get(
                "/products"
            )
            data = json.loads(response.data)
            self.assertEqual(len(data), 3)
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
