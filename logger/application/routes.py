from flask import request, jsonify, abort
from flask import current_app as app
from .models import Log
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import jwt
from application.messaging_producer import send_message
import requests
from jwt.exceptions import ExpiredSignatureError, DecodeError
from Crypto.PublicKey.RSA import import_key
import json
s=requests.Session()
response = s.get("http://auth:8000/client/get_public_key")
auth_public_key = json.loads(response.content)['public_key']
s.close()


# Delivery Routes ######################################################################################################
@app.route('/logger', methods=['GET'])
def view_logs():
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), auth_public_key, algorithms=["RS256"])
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
    session = Session()
    logs = session.query(Log).all()
    if not logs:
        abort(NotFound.code)
    response = jsonify(Log.list_as_dict(logs))
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


