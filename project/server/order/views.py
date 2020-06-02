# project/server/order/views.py

from flask import make_response, jsonify, Blueprint, request
from http import HTTPStatus
from datetime import datetime

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

# delete() - delete order <order_id> (SET ORDER STATUS ON CANCELLED FOR STATISTICS PUROPOSES)
# return 200 if order deleted
# return 404 if order is not exist
@order_blueprint.route("/orders/<int:order_id>", methods=["DELETE"])
@login_required
def delete(order_id):
    order_to_delete_result = Order.query.filter(Order.user_id == current_user.id).filter(Order.id == order_id).first()

    if order_to_delete_result:
        order_to_delete_result.status = Order.STATUS.CANCELLED
        db.session.commit()

        return make_response(jsonify({'message': 'Order cancelled'})), HTTPStatus.OK
    else:
        return make_response(jsonify({'message': 'Order is not exists'})), HTTPStatus.NOT_FOUND

# put() - update order <order_id> (SET ORDER STATUS ON CANCELLED FOR STATISTICS PUROPOSES)
# return 200 if order updated
# return 404 if order is not exist
@order_blueprint.route("/orders/<int:order_id>", methods=["PUT"])
@login_required
def put(order_id):
    order_to_update_result = Order.query.filter(Order.user_id == current_user.id)\
        .filter(Order.id == order_id).first()
    post_data = request.get_json()

    if order_to_update_result:
        if post_data:
            order_to_update_result.number = post_data['number']
            order_to_update_result.status = post_data['status']
            order_to_update_result.modification_date_gmt = datetime.utcnow()

            db.session.commit()

            OrderItem.query.filter(OrderItem.order_id == order_id).delete(synchronize_session=False)

            order_items = post_data['order_items']
            for order_item in order_items:
                oi = OrderItem()
                oi.product_id = order_item['product_id']
                oi.quantity = order_item['quantity']
                oi.order_id = order_id
                db.session.add(oi)
            db.session.commit()

            return make_response(jsonify({'message': 'Order updated'})), HTTPStatus.OK
        else:
            return make_response(jsonify({'message': 'No data to update order'})), HTTPStatus.OK
    else:
        return make_response(jsonify({'message': 'Order is not exists'})), HTTPStatus.NOT_FOUND