# project/server/order/views.py

from flask import make_response, jsonify, Blueprint, request
from http import HTTPStatus

from flask_login import login_required
from flask_login import current_user

from project.server import db
from project.server.models import Order, OrderItem

order_blueprint = Blueprint("order", __name__)

# post() - create new order for user
# return 201 if order created
# return 404 if no order data in request
@order_blueprint.route("/orders", methods=["POST"])
@login_required
def post():
    post_data = request.get_json()
    if post_data:
        user = current_user

        order = Order()
        order.number = post_data['number']
        order.user_id = user.id
        db.session.add(order)
        db.session.commit()

        order_items = post_data['order_items']

        for order_item in order_items:
            oi = OrderItem()
            oi.product_id = order_item['product_id']
            oi.quantity = order_item['quantity']
            oi.order_id = order.id
            db.session.add(oi)
        db.session.commit()

        return make_response(jsonify({'message': 'Order added'})), HTTPStatus.CREATED
    else:
        return make_response(jsonify({'message': 'No order params'})), HTTPStatus.NOT_FOUND