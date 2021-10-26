from flask import request, jsonify, abort
from flask import current_app as app
from .models import Deposit
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
from app import auth_public_key


# Order Routes #########################################################################################################

@app.route('/create_deposit', methods=['POST'])
def create_deposit():
    session = Session()
    new_deposit = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    try:
        new_deposit = Deposit(
            client_id=content['client_id'],
            balance=0
        )
        session.add(new_deposit)
        session.commit()
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)
    response = jsonify(new_deposit.as_dict())
    session.close()
    return response


@app.route('/payment/<int:deposit_id>', methods=['GET'])
def view_deposit(deposit_id):
    session = Session()
    deposit = session.query(Deposit).get(deposit_id)
    if not deposit:
        abort(NotFound.code)
    print("GET Deposit {}: {}".format(deposit_id, deposit))
    response = jsonify(deposit.as_dict())
    session.close()
    return response


@app.route('/payment', methods=['POST'])
def change_deposit():
    session = Session()
    deposit = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    deposit = session.query(Deposit).filter(Deposit.client_id == content['client_id']).one()
    if not deposit:
        abort(NotFound.code)
    deposit.balance += content['amount']
    session.commit()
    response = jsonify(deposit.as_dict())
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


