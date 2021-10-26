from Crypto.PublicKey.RSA import import_key
from flask import request, jsonify, abort
from flask import current_app as app
from .models import Client
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, InternalServerError, BadRequest, Unauthorized, UnsupportedMediaType
import traceback
from . import Session
import bcrypt
import jwt
from .crypto import rsa_singleton
import json
import base64
import datetime
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Order Routes #########################################################################################################
@app.route('/client', methods=['POST'])
def create_client():
    session = Session()
    new_client = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    
    #header = request.headers['Authorization'].replace("Bearer ", "").split(".")[0]
    #header = header + '=' * (4 - len(header) % 4) if len(header) % 4 != 0 else header

    #signature = request.headers['Authorization'].replace("Bearer ", "").split(".")[2]
    #signature = signature + '=' * (4 - len(signature) % 4) if len(signature) % 4 != 0 else signature

    response = requests.get("http://auth:8000/client/get_public_key")
    key = json.loads(response.content)['public_key']

    decodedJWT = jwt.decode(request.headers['Authorization'].replace("Bearer ", ""), key,algorithms=["RS256"])
    
    if decodedJWT['role'] != "admin":
         abort(Forbidden.code)
    
    content = request.json
    try:
        new_client = Client(
            username=content['username'],
	        password=bcrypt.hashpw(content['password'].encode(), bcrypt.gensalt()).decode('utf-8'),
	#     #password = content['password'],
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
    return response

@app.route('/client', methods=['GET'])
@app.route('/clients', methods=['GET'])
def view_clients():
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
        response = {
            'jwt': jwt.encode(payload, rsa_singleton.get_private_key(), algorithm='RS256').decode("utf-8") 
        }
     
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



