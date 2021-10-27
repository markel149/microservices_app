from requests.models import DecodeError
from sqlalchemy.sql.elements import False_
from werkzeug.exceptions import abort
import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
import datetime
from flask import jsonify
import traceback

class Validatejwt(object):
    @staticmethod
    def validate_token(token, pub_key):
        # Parse token
        # Signature
        try: 
            decodedJWT = jwt.decode(token.replace("Bearer ", ""), pub_key, algorithms=["RS256"])
        except ExpiredSignatureError as e:
            return False
        except DecodeError as e:
            return False

        # Expiration
        if datetime.datetime.utcnow() > datetime.datetime.utcnow() + datetime.timedelta(minutes=30):
            return False
        return True

    @staticmethod
    def is_admin(token, pub_key):
        # Parse token
        # Signature
        try: 
            decodedJWT = jwt.decode(token.replace("Bearer ", ""), pub_key, algorithms=["RS256"])
        except ExpiredSignatureError as error:
            return False
        except DecodeError as error:
            return False

        # Admin check
        if decodedJWT['role'] != "admin":
            return False
        return True
        
            
    
                
        
