# project/server/product/views.py

from flask import Blueprint
from flask import make_response, jsonify
from http import HTTPStatus

from project.server.models import Product

product_blueprint = Blueprint("product", __name__)

@product_blueprint.route("/products", methods=["GET"])
def get():
    products = Product.query.all()
    result = []

    if products:
        for product in products:
            result.append({
                'name': product.name,
                'permalink': product.permalink,
                'description': product.description,
                'price': product.price,
                'weight': product.weight
            })

        return make_response(jsonify(result)), HTTPStatus.OK

    return make_response(jsonify({'message': 'No products found'})), HTTPStatus.NOT_FOUND
