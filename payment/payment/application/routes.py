from flask import request, jsonify, abort
from flask import current_app as app
from .models import Payment
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session


# Order Routes #########################################################################################################
@app.route('/payment', methods=['POST'])
def create_payment():
    session = Session()
    new_payment = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    try:
        new_payment = Payment(
            payment=content['payment'],
            id_client=content['id_client']
        )
        session.add(new_payment)
        session.commit()
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)
    response = jsonify(new_payment.as_dict())
    session.close()
    return response


@app.route('/payment', methods=['GET'])
@app.route('/payments', methods=['GET'])
def view_orders():
    session = Session()
    print("GET All Orders.")
    payments = session.query(Payment).all()
    response = jsonify(Payment.list_as_dict(payments))
    session.close()
    return response


@app.route('/order/<int:payment_id>', methods=['GET'])
def view_order(payment_id):
    session = Session()
    payment = session.query(Payment).get(payment_id)
    if not payment:
        abort(NotFound.code)
    print("GET Payment {}: {}".format(payment_id, payment))
    response = jsonify(payment.as_dict())
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


