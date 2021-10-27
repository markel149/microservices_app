from flask import request, jsonify, abort
from flask import current_app as app
from .models import Order
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import json
from application.messaging_producer import send_message
import requests


s=requests.Session()
response = s.get("http://auth:8000/client/get_public_key")
auth_public_key = json.loads(response.content)['public_key']
s.close()

# Order Routes #########################################################################################################
@app.route('/order', methods=['POST'])
def create_order():
    return auth_public_key
    session = Session()
    new_order = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), auth_public_key, algorithms=["RS256"])
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
    
    content = request.json
    try:
        new_order = Order(
            client_id=content['client_id'],
            description=content['description'],
            number_of_pieces=content['number_of_pieces']
        )
        session.add(new_order)
        session.commit()
        message_body = {
            'order_id': new_order.order_id,
            'client_id': new_order.client_id,
            'number_of_pieces': new_order.number_of_pieces
        }
        send_message(exchange_name='event_exchange', routing_key='order.order_created', message=json.dumps(message_body))
        session.commit()
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)
    response = jsonify(new_order.as_dict())
    session.close()
    return response


@app.route('/order', methods=['GET'])
@app.route('/orders', methods=['GET'])
def view_orders():
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), auth_public_key, algorithms=["RS256"])
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
    session = Session()
    print("GET All Orders.")
    orders = session.query(Order).all()
    response = jsonify(Order.list_as_dict(orders))
    session.close()
    return response


@app.route('/order/<int:order_id>', methods=['GET'])
def view_order(order_id):
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), auth_public_key, algorithms=["RS256"])
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
    session = Session()
    order = session.query(Order).get(order_id)
    if not order:
        abort(NotFound.code)
    print("GET Order {}: {}".format(order_id, order))
    response = jsonify(order.as_dict())
    session.close()
    return response


@app.route('/order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    session = Session()
    order = session.query(Order).get(order_id)
    if not order:
        session.close()
        abort(NotFound.code)
    print("DELETE Order {}.".format(order_id))
    session.delete(order)
    session.commit()
    response = jsonify(order.as_dict())
    session.close()
    return response


# Error Handling #######################################################################################################
@app.errorhandler(UnsupportedMediaType)
def unsupported_media_type_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(BadRequest)
def bad_request_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(NotFound)
def resource_not_found_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(InternalServerError)
def server_error_handler(e):
    return get_jsonified_error(e)


def get_jsonified_error(e):
    traceback.print_tb(e.__traceback__)
    return jsonify({"error_code":e.code, "error_message": e.description}), e.code


