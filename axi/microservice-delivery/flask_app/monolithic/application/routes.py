from flask import request, jsonify, abort
from flask import current_app as app
from .models import Delivery
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session


# Delivery Routes ######################################################################################################
# TODO get delivery info
@app.route('/delivery/<int:delivery_id>', methods=['GET'])
def view_deposit(delivery_id):
    session = Session()
    delivery = session.query(Delivery).get(delivery_id)
    if not delivery:
        abort(NotFound.code)
    print("GET Deposit {}: {}".format(delivery_id, delivery))
    response = jsonify(delivery.as_dict())
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


