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

# get() - get existing user orders (ON PENDING STATUS)
# return 200 if orders exist
# return 404 if user has no orders

@order_blueprint.route("/orders", methods=["GET"])
@login_required
def get():
    pending_orders_result = Order.query.filter(Order.user_id == current_user.id)\
        .filter(Order.status == Order.STATUS.PENDING).all()

    response = []

    if pending_orders_result:
        for order in pending_orders_result:
            order_items = []

            for order_item in order.order_items:
                order_items.append({
                    'order_item_id': order_item.id,
                    'product_id': order_item.product_id,
                    'quantity': order_item.quantity,
                })

            response.append({
                'user_id': order.user_id,
                'orders': [{
                    'order_id': order.id,
                    'order_number': order.number,
                    'status': order.status.name,
                    'date_created_gmt': order.date_created_gmt,
                    'modification_date_gmt': order.modification_date_gmt,
                    'order_items': order_items
                }],
                'order_total': order.total()
            })

        return make_response(jsonify(response)), HTTPStatus.OK
    else:
        return make_response(jsonify({'message': 'No active orders exists'})), HTTPStatus.NOT_FOUND