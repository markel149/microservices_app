from Crypto.PublicKey.RSA import import_key
from flask import request, jsonify, abort
from flask import current_app as app
from .models import Client
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, InternalServerError, BadRequest, Unauthorized, UnsupportedMediaType
import traceback
from . import Session
import bcrypt
import jwt
import secrets
from .crypto import rsa_singleton
import json
import base64
import datetime
import requests
from application.messaging_producer import send_message
from jwt.exceptions import ExpiredSignatureError, DecodeError
 
message_body = {
    "public_key": rsa_singleton.get_public_key().decode('utf-8')
}
send_message(exchange_name='event_exchange', routing_key='auth.pub_key', message=json.dumps(message_body))
send_message(exchange_name='event_exchange', routing_key='auth.pub_key2', message=json.dumps(message_body))

# Order Routes #########################################################################################################
@app.route('/client', methods=['POST'])
def create_client():
    session = Session()
    new_client = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), rsa_singleton.get_public_key(), algorithms=["RS256"])
        if decodedJWT['role'] != "admin":
            abort(Forbidden.code)
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
    
    content = request.json
    try:
        new_client = Client(
            username=content['username'],
            password=bcrypt.hashpw(content['password'].encode(), bcrypt.gensalt()).decode('utf-8'),
            # password = content['password'],
            role=content['role']
        )

        session.add(new_client)
        session.commit()

    except KeyError:
        session.rollback()
        abort(BadRequest.code)
        session.close()
    
    response = jsonify(new_client.as_dict())
    session.close()
    message_body = {
        'client_id': new_client.id
    }
    send_message(exchange_name='event_exchange', routing_key='client.client_created', message=json.dumps(message_body))
    return response

@app.route('/client', methods=['GET'])
@app.route('/clients', methods=['GET'])
def view_clients():
    try:
        decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), auth_public_key, algorithms=["RS256"])
    except ExpiredSignatureError as e:
        return jsonify({"error_message": "Token Expired"})
    except DecodeError as e:
        return jsonify({"error_message": "Decode Error"})
    session = Session()
    print("GET All Clients.")
    clients = session.query(Client).all()
    response = jsonify(Client.list_as_dict(clients))
    session.close()
    return response


@app.route('/client/create_jwt', methods=['GET'])
def create_jwt():
    session = Session()
    response = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    
    userpass = base64.b64decode(request.headers['Authorization'].replace("Basic ",""))
    userpass2 = userpass.decode('utf-8').split(":")
    username = userpass2[0]
    password = userpass2[1]  
    try:
        user = session.query(Client).filter(Client.username == username).one()

        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            raise Exception
        payload = {
            'id': user.id,
            'username': user.username,
            'service': False,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        refresh_token = secrets.token_urlsafe(16)
        user.refresh_token = refresh_token
        session.commit()
        response = {
            'jwt': jwt.encode(payload, rsa_singleton.get_private_key(), algorithm='RS256').decode("utf-8"),
            'refresh_token': refresh_token
        }
     
    except Exception as e:
      
        session.rollback()
        session.close()
        abort(BadRequest.code)
    
    session.close()
    return response


@app.route('/client/refresh_jwt', methods=['GET'])
def get_refreshed_jwt():
    session = Session()
    response = None
    received_refresh_token = request.headers['Authorization'].replace("Bearer ", "")
    content = request.json

    try:
        user = session.query(Client).filter(Client.username == content['username']).one()
        if not user:
            abort(NotFound.code)
        if user.refresh_token == received_refresh_token:
            payload = {
                'id': user.id,
                'username': user.username,
                'service': False,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }
            response = {
                'jwt': jwt.encode(payload, rsa_singleton.get_private_key(), algorithm='RS256').decode("utf-8")
            }
        else:
            abort(BadRequest.code)

    except Exception as e:

        session.rollback()
        session.close()
        abort(BadRequest.code)

    session.close()
    return response


@app.route('/client/get_public_key', methods=['GET'])
def get_public_key():
    content = {}
    content['public_key'] = rsa_singleton.get_public_key().decode()
    return content  

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

@app.errorhandler(Forbidden)
def server_error_handler(e):
    return get_jsonified_error(e)


def get_jsonified_error(e):
    traceback.print_tb(e.__traceback__)
    return jsonify({"error_code":e.code, "error_message": e.description}), e.code



