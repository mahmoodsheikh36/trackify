from flask import Flask, jsonify, request, Blueprint, current_app, g
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, jwt_refresh_token_required
)

from trackify.webapp.auth import try_credentials
from trackify.utils import get_largest_elements, timestamp_to_date, current_time

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

@bp.route('/history', methods=('GET',))
@jwt_required
def history():
    hrs_limit = request.args.get('hrs_limit', 24*7)
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
    hrs_str = request.args.get('hrs', default='24,{},{}'.format(24*7, 24*30), type=str)
    hrs = []
    for hr_str in hrs_str.split(','):
        try:
            hrs.append(int(hr_str))
        except:
            return jsonify({'msg': "'hrs' should be a list of comma-separated integers"}), 401
    oldest_hr = hrs[0]
    for i in range(len(hrs)):
        try:
            hrs[i] = int(hrs[i])
        except:
            return jsonify({'msg': "'hrs' should be an array of positive integers"}), 401
        if hrs[i] <= 0:
            return jsonify({'msg': "'hrs' should be an array of positive integers"}), 401
        if hrs[i] > oldest_hr:
            oldest_hr = hrs[i]

    begin_time = current_time() - oldest_hr * 3600 * 1000

    artists, albums, tracks, plays = g.music_provider.get_user_data(get_user())

    data = {}
    for hr in hrs:
        begin_time = current_time() - hr * 3600 * 1000
        for play in plays.values():
           if hasattr(play.track, 'listened_ms'):
               play.track.listened_ms += play.listened_ms(begin_time)
           else:
               play.track.listened_ms = play.listened_ms(begin_time)

        def compare(track1, track2):
            return track1.listened_ms > track2.listened_ms

        top_tracks = get_largest_elements(list(tracks.values()), 20, compare)

        data[hr] = []
        for track in top_tracks:
            if track.listened_ms == 0:
                continue
            data[hr].append({
                'id': track.id,
                'name': track.name,
                'listened_ms': track.listened_ms,
                'artist': {
                    'name': track.artists[0].name,
                    'id': track.artists[0].id
                },
                'album': {
                    'id': track.album.id,
                    'cover': track.album.mid_sized_image().url,
                    'name': track.album.name,
                }
            })

    return jsonify(data)

@bp.route('/top_users', methods=('GET',))
@jwt_required
def top_users():
    from_time = request.args.get('from_time', default=0, type=int)
    to_time = request.args.get('to_time', default=9999999999999, type=int)
    if from_time < 0:
        return jsonify({"msg": "from_time should be a positive integer"}), 401
    if to_time < 0:
        return jsonify({"msg": "to_time should be a positive integer"}), 401

    limit = 10
    top_tracks_limit = 3

    users, artists, albums, tracks, plays =\
        g.music_provider.get_all_users_data(from_time, to_time)

    users_to_sort = []
    for user in users.values():
        if user.settings.get_by_name('show_on_top_users').value:
            if user.plays:
                users_to_sort.append(user)

    for user in users_to_sort:
        for play in user.plays:
            listened_ms = play.listened_ms(from_time, to_time)
            if hasattr(play.track, 'listened_ms'):
                if user.id in play.track.listened_ms:
                    play.track.listened_ms[user.id] += listened_ms
                else:
                    play.track.listened_ms[user.id] = listened_ms
            else:
                play.track.listened_ms = {user.id: listened_ms}
            if not hasattr(user, 'listened_ms'):
                user.listened_ms = listened_ms
            else:
                user.listened_ms += listened_ms
            if hasattr(user, 'top_tracks'):
                if not play.track in user.top_tracks:
                    added = False
                    for idx, track in enumerate(user.top_tracks):
                        if track.listened_ms[user.id] < play.track.listened_ms[user.id]:
                            user.top_tracks.insert(idx, play.track)
                            added = True
                            if len(user.top_tracks) > top_tracks_limit:
                                del user.top_tracks[-1]
                            break
                    if not added:
                        if len(user.top_tracks) < top_tracks_limit:
                            user.top_tracks.append(play.track)
                else:
                    idx = user.top_tracks.index(play.track)
                    for i in range(idx):
                        if play.track.listened_ms[user.id] > user.top_tracks[i].listened_ms[user.id]:
                            user.top_tracks[idx], user.top_tracks[i] = user.top_tracks[i], user.top_tracks[idx]
                            break
            else:
                user.top_tracks = [play.track]

    def compare(user1, user2):
        if not hasattr(user1, 'listened_ms'):
            return False
        if not hasattr(user2, 'listened_ms'):
            return True
        return user1.listened_ms > user2.listened_ms
    top_users = get_largest_elements(users_to_sort, limit, compare)

    return jsonify([{
        'username': user.username,
        'listened_ms': user.listened_ms,
        'top_tracks': [{
            'listened_ms': track.listened_ms[user.id],
            'id': track.id,
            'name': track.name,
            'artists': [{
                'id': artist.id,
                'name': artist.name,
            } for artist in track.artists],
            'album': {
                'id': track.album.id,
                'name': track.album.name,
                'covers': [{
                    'url': cover.url,
                    'width': cover.width,
                    'height': cover.height
                } for cover in track.album.images],
                'artists': [{
                    'id': artist.id,
                    'name': artist.name
                } for artist in track.album.artists]
            }
        } for track in user.top_tracks]
    } for user in top_users])

@bp.route('/track_history', methods=('GET',))
@jwt_required
def track_history():
    hrs_limit = request.args.get('hrs_limit', default=24*7, type=int)
    if hrs_limit < 1:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401
    track_id = request.args.get('track_id')

    from_time = current_time() - hrs_limit * 3600 * 1000

    plays = g.music_provider.get_user_track_plays(get_user(), from_time=from_time, track_id=track_id)

    data = []
    for play in plays:
        data.append({
            #'id': play.id,
            'listened_ms': play.listened_ms(from_time=from_time),
            'play_time': timestamp_to_date(play.time_started).strftime('%Y-%m-%d %H:%M:%S'),
        })

    return jsonify(data)

@bp.route('/data', methods=('GET',))
@jwt_required
def data():
    from_time = request.args.get('from_time', default=0, type=int)
    to_time = request.args.get('to_time', default=9999999999999, type=int)
    if from_time < 0:
        return jsonify({"msg": "from_time should be a positive integer"}), 401
    if to_time < 0:
        return jsonify({"msg": "to_time should be a positive integer"}), 401

    user = get_user()
    artists, albums, tracks, plays = g.music_provider.get_user_data(user,
                                                                    from_time=from_time,
                                                                    to_time=to_time)
    data = {
        'plays': [
        ],
    }
    for play in plays.values():
        data['plays'].append({
            'id': play.id,
            'time_started': play.time_started,
            'time_ended': play.time_ended,
            'track': {
                'id': play.track.id,
                'name': play.track.name,
                'artists': [{
                    'id': artist.id,
                    'name': artist.name,
                } for artist in play.track.artists],
                'album': {
                    'id': play.track.album.id,
                    'name': play.track.album.name,
                    'covers': [{
                        'url': cover.url,
                        'width': cover.width,
                        'height': cover.height
                    } for cover in play.track.album.images],
                    'artists': [{
                        'id': artist.id,
                        'name': artist.name
                    } for artist in play.track.album.artists]
                }
            },
            'pauses': [{
                'id': pause.id,
                'time_added': pause.time_added,
            } for pause in play.pauses],
            'resumes': [{
                'id': resume.id,
                'time_added': resume.time_added,
            } for resume in play.resumes]
        })

    return jsonify(data)
