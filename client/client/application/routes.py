from flask import request, jsonify, abort
from flask import current_app as app
from .models import Client
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session


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
            name=content['name'],
            surname=content['surname'],
            username=content['username'],
            status=Client.STATUS_CREATED
        )
        session.add(new_client)
        session.commit()
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)
    response = jsonify(new_client.as_dict())
    session.close()
    return response


@app.route('/client', methods=['GET'])
@app.route('/clients', methods=['GET'])
def view_orders():
    session = Session()
    print("GET All Orders.")
    orders = session.query(Client).all()
    response = jsonify(Client.list_as_dict(orders))
    session.close()
    return response


@app.route('/order/<int:client_id>', methods=['GET'])
def view_order(client_id):
    session = Session()
    client = session.query(Client).get(client_id)
    if not client:
        abort(NotFound.code)
    print("GET Client {}: {}".format(client_id, client))
    response = jsonify(client.as_dict())
    session.close()
    return response


@app.route('/order/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    session = Session()
    client = session.query(Client).get(client_id)
    if not client:
        session.close()
        abort(NotFound.code)
    print("DELETE Client {}.".format(client_id))
    session.delete(client)
    session.commit()
    response = jsonify(client.as_dict())
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


