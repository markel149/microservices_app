from flask import request, jsonify, abort
from flask import current_app as app
from .models import Log
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session

response = requests.get("http://auth:8000/client/get_public_key")
global auth_public_key
auth_public_key = json.loads(response.content)['public_key']

# Delivery Routes ######################################################################################################
@app.route('/logger', methods=['GET'])
def view_logs():
    session = Session()
    logs = session.query(Log).all()
    if not logs:
        abort(NotFound.code)
    response = jsonify(Log.list_as_dict(logs))
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


