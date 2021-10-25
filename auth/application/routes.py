from flask import request, jsonify, abort
from flask import current_app as app
from .models import Client
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import bcrypt
import jwt
from .crypto import rsa_singleton

# Order Routes #########################################################################################################
@app.route('/client', methods=['POST'])
def create_client():
    session = Session()
    new_client = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    try:
        new_client = Client(
            username=content['username'],
	    #password=bcrypt.hashpw(content['password'].encode(), bcrypt.gensalt()).decode('utf-8'),
	    password = content['password'],
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

@app.route('/client/get_jwt', methods=['GET'])
def get_jwt():
    session = Session()
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    response = None
    try: 
        user = session.query(Client).filter(Client.id == content['id']).one()
        #if not bcrypt.checkpw(content['password'].encode('utf-8'), user.password.encode('utf-8')):
        if not user.password == content['password']:
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



