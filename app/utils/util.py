from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
import jose
from functools import wraps
from flask import request, jsonify
import os



SECRET_KEY = os.environ.get('SECRET_KEY') or "a super secret, secret key"


def encode_token(customer_id): 
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:

            token = request.headers['Authorization'].split()[1]

            if not token:
                return jsonify({'message': 'missing token'}), 400

            try:

                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                print(data)
                customer_id = int(data['sub'])
            except ExpiredSignatureError:
                return jsonify({'message': 'token expired!'}), 400
            except JWTError:
                return jsonify({'message': 'token is invalid!'}), 400

            return f(customer_id, *args, **kwargs)

        else:
            return jsonify({'message': 'You must be logged in to access this.'}), 400

    return decorated


def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:

            token = request.headers['Authorization'].split()[1]

            if not token:
                return jsonify({'message': 'missing token'}), 400

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                mechanic_id = int(data['sub'])
            except ExpiredSignatureError:
                return jsonify({'message': 'token expired!'}), 400
            except JWTError:
                return jsonify({'message': 'token is invalid!'}), 400

            return f(mechanic_id, *args, **kwargs)

        else:
            return jsonify({'message': 'You must be logged in to access this.'}), 400

    return decorated
            
            