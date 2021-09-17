from flask import request, g, jsonify

def access_token_required(func):
    def wrapper():
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({"msg": "auth header wasnt provided"}), 401
        arr = auth_header.split(' ')
        if len(arr) != 2:
            return jsonify({"msg": "incorrect auth header"}), 401
        token_id = arr[1]
        token = g.db_data_provider.get_api_access_token(token_id)
        if not token:
            return jsonify({"msg": "access token doesnt exist"}), 401
        if token.expired():
            return jsonify({"msg": "access token has expirede"}), 401
        return func()
    wrapper.__name__ = func.__name__ # to avoid an error
    return wrapper

def refresh_token_required(func):
    def wrapper():
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({"msg": "auth header wasnt provided"}), 401
        arr = auth_header.split(' ')
        if len(arr) != 2:
            return jsonify({"msg": "incorrect auth header"}), 401
        token_id = arr[1]
        token = g.db_data_provider.get_api_refresh_token(token_id)
        if token is None:
            return jsonify({"msg": "refresh token doesnt exist"}), 401
        return func()
    wrapper.__name__ = func.__name__ # to avoid an error
    return wrapper

def get_user():
    auth_header = request.headers.get('Authorization')
    arr = auth_header.split(' ')
    if len(arr) != 2:
        return None
    token_id = arr[1]
    token = g.db_data_provider.get_api_access_token(token_id)
    return token.refresh_token.user

def get_refresh_token():
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return None
    arr = auth_header.split(' ')
    if len(arr) != 2:
        return None
    token_id = arr[1]
    token = g.db_data_provider.get_api_refresh_token(token_id)
    return token
    
