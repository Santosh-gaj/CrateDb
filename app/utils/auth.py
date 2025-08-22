from functools import wraps
from flask import request, jsonify
import jwt
from app.config import config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
            request.transporter_id = data['sub']
        except Exception as e:
            return jsonify({'error': f'Invalid or expired token: {str(e)}'}), 401

        return f(*args, **kwargs)
    return decorated
