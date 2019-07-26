'''JWT token generation'''
from datetime import datetime, timedelta
import jwt
from messenger.settings import SECRET_KEY

class TokenGenerator:
    '''Generates a jwt token'''
    @classmethod
    def generate(cls, email):
        '''Encoding of the token using the user email'''
        payload = {
            'email': email,
            'exp': datetime.utcnow() + timedelta(minutes=60)
        }
        return jwt.encode(payload, SECRET_KEY,
                          algorithm='HS256').decode('utf-8')
