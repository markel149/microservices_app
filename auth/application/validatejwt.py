from requests.models import DecodeError
from sqlalchemy.sql.elements import False_
from werkzeug.exceptions import abort
import jwt
import datetime


class validation(object):
    @staticmethod
    def validate_token(token):
        # Parse token
        # Signature
        try: 
            decodedJWT = jwt.decode(token.replace("Bearer ", ""), ,algorithms=["RS256"])
        except Exception as e:
            abort(DecodeError)

        # Expiration
        if datetime.datetime.utcnow() > datetime.datetime.utcnow() + datetime.timedelta(minutes=30):
            return False
        return True

    @staticmethod
    def is_admin(token):
        # Parse token
        # Signature
        try: 
            decodedJWT = jwt.decode(token.replace("Bearer ", ""), ,algorithms=["RS256"])
        except Exception as e:
            abort(DecodeError)

        # Admin check
        if decodedJWT['role'] != "admin":
            return False
        return True
        
            
    
                
        
