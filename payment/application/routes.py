from flask import request, jsonify, abort
from flask import current_app as app
from .models import Deposit
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import requests
import json
import jwt
import requests
from jwt.exceptions import ExpiredSignatureError, DecodeError
from Crypto.PublicKey.RSA import import_key

s=requests.Session()
response = s.get("http://auth:8000/client/get_public_key")
auth_public_key = json.loads(response.content)['public_key']
s.close()

# Order Routes #########################################################################################################

@app.route('/create_deposit', methods=['POST'])
def create_deposit():
    #global auth_public_key
    #return auth_public_key
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), auth_public_key, algorithms=["RS256"])
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
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
    deposit = session.query(Deposit).filter(Deposit.client_id == content['client_id']).first()
    if not deposit:
        abort(NotFound.code)
    deposit.balance += content['amount']
    session.commit()
    response = jsonify(deposit.as_dict())
    session.close()
    return response

@app.route('/health', methods=['HEAD', 'GET']) 
def health_check():
#abort(BadRequest)
    return "OK"

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


