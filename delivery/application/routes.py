from flask import request, jsonify, abort
from flask import current_app as app
from .models import Delivery
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session

import jwt
from application.messaging_producer import send_message
import requests
from jwt.exceptions import ExpiredSignatureError, DecodeError
from Crypto.PublicKey.RSA import import_key

s=requests.Session()
response = s.get("http://auth:8000/client/get_public_key")
auth_public_key = json.loads(response.content)['public_key']
s.close()
# Delivery Routes ######################################################################################################
# TODO get delivery info
@app.route('/delivery/<int:delivery_id>', methods=['GET'])
def view_deposit(delivery_id):
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), auth_public_key, algorithms=["RS256"])
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
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


