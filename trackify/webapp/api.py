from flask import Flask, jsonify, request, Blueprint, current_app, g
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, jwt_refresh_token_required
)

from trackify.webapp.auth import try_credentials
from trackify.utils import get_largest_elements, timestamp_to_date, current_time, get_user_setting_by_name

bp = Blueprint('api', __name__, url_prefix='/api')

def get_user():
    username = get_jwt_identity()
    return g.music_provider.get_user_by_username(username)

@bp.route('/login', methods=('POST',))
def login():
    if not 'username' in request.form:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not 'password' in request.form:
        return jsonify({"msg": "Missing password parameter"}), 400

    username = request.form['username']
    password = request.form['password']

    if not try_credentials(username, password):
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
    hrs_limit = request.args.get('hrs_limit', default=24*1000)
    try:
        hrs_limit = int(hrs_limit)
    except:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401
    if hrs_limit < 1:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401

    begin_time = current_time() - hrs_limit * 3600 * 1000

    artists, albums, tracks, plays = g.music_provider.get_user_data(get_user())

    plays_to_sort = []
    for play in plays.values():
        if play.time_started > begin_time:
            plays_to_sort.append(play)
            
    def compare(play1, play2):
        return play1.time_started > play2.time_started
    sorted_plays = get_largest_elements(plays_to_sort, -1, compare)

    data = []
    for play in sorted_plays:
        data.append({
            'id': play.id,
            'play_time': timestamp_to_date(play.time_started).strftime('%Y-%m-%d %H:%M:%S'),
            'track': {
                'id': play.track.id,
                'name': play.track.name,
                'artist': {
                    'name': play.track.artists[0].name,
                    'id': play.track.artists[0].id
                },
                'album': {
                    'id': play.track.album.id,
                    'cover': play.track.album.smallest_image().url,
                    'name': play.track.album.name,
                }
            },
        })

    return jsonify(data)

@bp.route('/top_tracks', methods=('GET',))
@jwt_required
def top_track():
    hrs_limit = request.args.get('hrs_limit', 24 * 7)
    try:
        hrs_limit = int(hrs_limit)
    except:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401

    if hrs_limit == 0:
        begin_time = None
    else:
        begin_time = current_time() - hrs_limit * 3600 * 1000

    if begin_time and begin_time < 0:
        begin_time = 0

    artists, albums, tracks, plays = g.music_provider.get_user_data(get_user())

    for play in plays.values():
        if hasattr(play.track, 'listened_ms'):
            play.track.listened_ms += play.listened_ms(begin_time)
        else:
            play.track.listened_ms = play.listened_ms(begin_time)

    def compare(track1, track2):
        return track1.listened_ms > track2.listened_ms

    top_tracks = get_largest_elements(list(tracks.values()), 3, compare)

    tracks_to_return = []
    for track in top_tracks:
        tracks_to_return.append({
            'id': track.id,
            'name': track.name,
            'listened_ms': track.listened_ms,
            'artist': {
                'name': track.artists[0].name,
                'id': track.artists[0].id
            },
            'album': {
                'id': track.album.id,
                'cover': track.album.smallest_image().url,
                'name': track.album.name,
            }
        })

    return jsonify(tracks_to_return)

@bp.route('/top_users', methods=('GET',))
@jwt_required
def top_users():
    hrs_limit = request.args.get('hrs_limit', 24 * 7)
    try:
        hrs_limit = int(hrs_limit)
    except:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401

    if hrs_limit == 0:
        begin_time = None
    else:
        begin_time = current_time() - hrs_limit * 3600 * 1000

    if begin_time and begin_time < 0:
        begin_time = 0

    users = g.music_provider.get_users()
    LIMIT = 10

    users_to_sort = []
    for idx, user in enumerate(users):
        user_settings = g.music_provider.get_user_settings(user)
        if not get_user_setting_by_name(user_settings, 'show_on_top_users').value:
            continue
        user.show_favorite_track =\
            get_user_setting_by_name(user_settings,
                                     'show_favorite_track_on_top_users').value
        artists, albums, tracks, plays = g.music_provider.get_user_data(user)
        if not plays:
            continue
        for play in plays.values():
            listened_ms = play.listened_ms(begin_time)
            if hasattr(play.track, 'listened_ms'):
                play.track.listened_ms += listened_ms
            else:
                play.track.listened_ms = listened_ms
            if not hasattr(user, 'top_track') or\
               play.track.listened_ms > user.top_track.listened_ms:
                user.top_track = play.track
            if not hasattr(user, 'listened_ms'):
                user.listened_ms = listened_ms
            else:
                user.listened_ms += listened_ms
        if user.listened_ms:
            users_to_sort.append(user)

    def compare(user1, user2):
        if not hasattr(user1, 'listened_ms'):
            return False
        if not hasattr(user2, 'listened_ms'):
            return True
        return user1.listened_ms > user2.listened_ms
    top_users = get_largest_elements(users_to_sort, LIMIT, compare)

    users_to_return = []
    for user in top_users:
        users_to_return.append({
            'username': user.username,
            'listened_ms': user.listened_ms,
        })

    return jsonify(users_to_return)
