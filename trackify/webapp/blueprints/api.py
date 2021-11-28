from flask import Flask, jsonify, request, Blueprint, current_app, g
import requests

from trackify.utils import get_largest_elements, timestamp_to_date, current_time, one_week_ago
from trackify.webapp.jwt import access_token_required, refresh_token_required, get_user, get_refresh_token
import config

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.after_request
def after_request(response):
    response.headers.set('Access-Control-Allow-Origin', '*')
    return response

@bp.route('/login', methods=('POST',))
def login():
    if not 'username' in request.form:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not 'password' in request.form:
        return jsonify({"msg": "Missing password parameter"}), 400

    username = request.form['username']
    password = request.form['password']

    user = g.db_data_provider.get_user_by_credentials(username, password)
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    refresh_token = g.db_data_provider.create_api_refresh_token(user)
    access_token = g.db_data_provider.create_api_access_token(refresh_token)
    return jsonify({
        'access_token': {
            'id': access_token.id,
            'expiry_time': access_token.expiry_time()
        },
        'refresh_token': {
            'id': refresh_token.id,
        }
    })

@bp.route('/refresh', methods=('POST',))
@refresh_token_required
def refresh():
    refresh_token = get_refresh_token()
    new_access_token = g.db_data_provider.create_api_access_token(refresh_token)
    return jsonify({
        'access_token': {
            'id': new_access_token.id,
            'expiry_time': new_access_token.expiry_time()
        }
    })

@bp.route('/protected', methods=('GET',))
@access_token_required
def protected():
    return jsonify(logged_in_as=get_user().username), 200

@bp.route('/history', methods=('GET',))
@access_token_required
def history():
    hrs_limit = request.args.get('hrs_limit', 24*7)
    try:
        hrs_limit = int(hrs_limit)
    except:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401
    if hrs_limit < 1:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401

    begin_time = current_time() - hrs_limit * 3600 * 1000

    artists, albums, tracks, plays = g.db_data_provider.get_user_data(get_user())

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

@bp.route('/top_users', methods=('GET',))
@access_token_required
def top_users():
    from_time = request.args.get('from_time', default=current_time() - 1000 * 60 * 60 * 24,
                                 type=int)
    to_time = request.args.get('to_time', default=9999999999999, type=int)
    if from_time < 0:
        return jsonify({"msg": "from_time should be a positive integer"}), 401
    if to_time < 0:
        return jsonify({"msg": "to_time should be a positive integer"}), 401

    limit = 10
    top_tracks_limit = 3

    users, artists, albums, tracks, plays =\
        g.db_data_provider.get_all_users_data(from_time, to_time)

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
@access_token_required
def track_history():
    hrs_limit = request.args.get('hrs_limit', default=24*7, type=int)
    if hrs_limit < 1:
        return jsonify({"msg": "hrs_limit should be a positive integer"}), 401
    track_id = request.args.get('track_id')

    from_time = current_time() - hrs_limit * 3600 * 1000

    plays = g.db_data_provider.get_user_track_plays(get_user(), from_time=from_time, track_id=track_id)

    data = []
    for play in plays:
        data.append({
            #'id': play.id,
            'listened_ms': play.listened_ms(from_time=from_time),
            'play_time': timestamp_to_date(play.time_started).strftime('%Y-%m-%d %H:%M:%S'),
        })

    return jsonify(data)

@bp.route('/data', methods=('GET',))
@access_token_required
def data():
    from_time = request.args.get('from_time', default=0, type=int)
    to_time = request.args.get('to_time', default=9999999999999, type=int)
    if from_time < 0:
        return jsonify({"msg": "from_time should be a positive integer"}), 401
    if to_time < 0:
        return jsonify({"msg": "to_time should be a positive integer"}), 401

    user = get_user()
    artists, albums, tracks, plays = g.db_data_provider.get_user_data(user,
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

@bp.route('/last_play', methods=('GET',))
def last_play():
    play = g.db_data_provider.get_last_play()
    return jsonify({
        'username': play.user.username,
        'time_played': play.time_started,
        'artist_name': play.track.artists[0].name,
        'track_name': play.track.name
    })


@bp.route('/top_artists', methods=('GET',))
def top_artists():
    num_of_artists_to_return = request.args.get('num_of_artists_to_return', default=10, type=int)
    if num_of_artists_to_return > 25:
        num_of_artists_to_return = 25
    top_artists = g.db_data_provider.get_top_artists(num_of_artists_to_return,
                                                     one_week_ago(), current_time())
    return jsonify([{
        'name': artist.name,
        'listened_ms': artist.listened_ms
    } for artist in top_artists])

@bp.route('/artist_discogs_data', methods=('GET',))
def artist_discogs_data():
    artist_name = request.args.get('artist_name', default=None, type=str)
    if not artist_name:
        return ''

    cached_data = g.cache_data_provider.get_artist_discogs_data(artist_name)
    if cached_data:
        return cached_data

    api_key = config.CONFIG['discogs_api_key']
    api_secret = config.CONFIG['discogs_api_secret']

    response = requests.get(f'https://api.discogs.com/database/search?q={artist_name}&type=artist&'
                            f'key={api_key}&secret={api_secret}')
    artist_data = {}
    try:
        artist_data = response.json()['results'][0]
    except KeyError: # if discogs returns no results
        pass

    g.cache_data_provider.set_artist_discogs_data(artist_name, artist_data)

    return jsonify(artist_data)

@bp.route('/top_tracks', methods=('GET',))
def top_tracks():
    num_of_tracks_to_return = request.args.get('num_of_tracks_to_return', default=5, type=int)
    if num_of_tracks_to_return > 25:
        num_of_tracks_to_return = 25
    top_tracks = g.db_data_provider.get_top_tracks(num_of_tracks_to_return,
                                                   one_week_ago(), current_time())
    return jsonify([{
        'name': track.name,
        'listened_ms': track.listened_ms,
        'image_url': track.album.smallest_image().url,
        'artist_name': track.artists[0].name
    } for track in top_tracks])

@bp.route('total_plays', methods=('GET',))
def total_plays():
    total_plays = g.db_data_provider.get_total_plays()
    return jsonify({
        'total': total_plays
    })
