from flask import Flask, jsonify, request, Blueprint, current_app, g
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, jwt_refresh_token_required
)

from trackify.webapp.auth import check_credentials
from trackify.utils import get_largest_elements, timestamp_to_date

bp = Blueprint('api', __name__, url_prefix='/api')

def get_user():
    username = get_jwt_identity()
    return g.music_provider.get_user_by_username(username)

@bp.route('/login', methods=('POST',))
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if not check_credentials(username, password):
        return jsonify({"msg": "Bad username or password"}), 401

    return jsonify({
        'access_token': create_access_token(identity=username),
        'refresh_token': create_refresh_token(identity=username)
    })

@bp.route('/refresh', methods=('POST',))
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    return jsonify({
        'access_token': create_access_token(identity=current_user)
    })

@bp.route('/protected', methods=('GET',))
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@bp.route('/random_track', methods=('GET',))
@jwt_required
def random_track():
    artists, albums, tracks, plays = g.music_provider.get_user_data(get_user())
    tracks = list(tracks.values())
    return jsonify({
        "name": tracks[0].name,
        "artist": tracks[0].artists[0].name,
        "album": tracks[0].album.name,
        "cover": tracks[0].album.images[0].url
    })

@bp.route('/history', methods=('GET',))
@jwt_required
def history():
    limit = request.args.get('limit')
    if not limit:
        limit = 50
    try:
        limit = int(limit)
    except:
        return jsonify({"msg": "limit must be an integer"}), 401
    if limit < 1:
        limit = 50
    if limit > 500:
        limit = 500

    artists, albums, tracks, plays = g.music_provider.get_user_data(get_user())
            
    def compare(play1, play2):
        return play1.time_started > play2.time_started
    sorted_plays = get_largest_elements(list(plays.values()), limit, compare)

    data = []
    for play in sorted_plays:
        data.append({
            'play_time': timestamp_to_date(play.time_started).strftime('%d/%m/%Y %H:%M:%S'),
            'name': play.track.name,
            'artist': play.track.artists[0].name,
            'cover': play.track.album.images[0].url,
            'album': play.track.album.name
        })

    return jsonify(data)
