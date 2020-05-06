import json

from trackify.db.db import DBProvider
from trackify.utils import current_time, generate_id

class Request:
    def __init__(self, flask_request):
        self.id = generate_id()
        if flask_request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            self.ip = flask_request.environ['REMOTE_ADDR']
        else:
            self.ip = flask_request.environ.get('HTTP_X_FORWARDED_FOR')
        self.headers = json.dumps({k:v for k, v in flask_request.headers.items()})
        self.data = flask_request.data.decode('UTF-8')
        self.form = json.dumps(flask_request.form.to_dict(flat=False), indent=2)
        self.access_route = json.dumps(flask_request.access_route, indent=2)
        self.referrer = flask_request.referrer
        self.url = flask_request.url
        self.time_added = current_time()

class User:
    def __init__(self, user_id, username, password, email, time_added,
                 access_token=None, refresh_token=None, plays=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.time_added = time_added
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.plays = plays

class Artist:
    def __init__(self, artist_id, name):
        self.id = artist_id
        self.name = name

class Track:
    def __init__(self, track_id, name, album, artists, duration_ms, popularity,
                 preview_url, track_number, explicit):
        self.id = track_id
        self.name = name
        self.album = album
        self.artists = artists
        self.duration_ms = duration_ms
        self.popularity = popularity
        self.preview_url = preview_url
        self.track_number = track_number
        self.explicit = explicit

class Album:
    def __init__(self, album_id, name, artists, images, album_type, release_date,
                 release_date_precision):
        self.id = album_id
        self.name = name
        self.type = album_type
        self.artists = artists
        self.images = images
        self.release_date = release_date
        self.release_date_precision = release_date_precision

class MusicProvider:
    def __init__(self, *args, **kwargs):
        self.db_provider = DBProvider(*args, **kwargs)

    def close(self):
        self.db_provider.close()

    def commit(self):
        self.db_provider.commit()

    def get_user_by_username(self, username):
        user_row = self.db_provider.get_user_by_username(username)
        if user_row:
            return User(user_row[0], user_row[1], user_row[2], user_row[3],
                        int(user_row[4]))
        return None

    def add_user(self, user):
        self.db_provider.add_user(user.id, user.username, user.password, user.email,
                                  user.time_added)
        self.commit()

    def add_request(self, request):
        self.db_provider.add_request(request.id, request.time_added, request.ip,
                                     request.url, request.headers, request.data,
                                     request.form, request.referrer, request.access_route)
        self.commit()

    def add_auth_code(self, code):
        self.db_provider.add_auth_code(code.id, code.time_added, code.code, code.user.id)
        self.commit()

    def add_access_token(self, t):
        self.db_provider.add_access_token(t.id, t.token, t.user.id, t.time_added)
        self.commit()

    def add_refresh_token(self, t):
        self.db_provider.add_refresh_token(t.id, t.token, t.user.id, t.time_added)
        self.commit()

    def get_user(self, user_id):
        user_row = self.db_provider.get_user(user_id)
        if user_row:
            return User(user_row[0], user_row[1], user_row[2], user_row[3],
                        int(user_row[4]))
        return None

    def get_user_auth_code(self, user):
        code_row = self.db_provider.get_user_auth_code(user.id)
        if code_row:
            return AuthCode(code_row[0], code_row[2], code_row[3], int(code_row[1]))
        return None

    def get_user_access_token(self, user):
        token_row = self.db_provider.get_user_access_token(user.id)
        if token_row:
            return AccessToken(token_row[0], token_row[2], user, int(token_row[1]))
        return None

    def get_user_refresh_token(self, user):
        token_row = self.db_provider.get_user_refresh_token(user.id)
        if token_row:
            return RefreshToken(token_row[0], token_row[2], user, int(token_row[1]))
        return None

    def get_users(self):
        user_rows = self.db_provider.get_users()
        users = []
        for user_row in user_rows:
            user = User(user_row[0], user_row[1], user_row[2], user_row[3],
                        int(user_row[4]))
            users.append(user)
        return users

    def get_users_with_tokens(self):
        rows = self.db_provider.get_users_with_tokens()
        users = []
        for row in rows:
            user = User(row[0], row[1], row[2], row[3], int(row[4]))
            user.access_token = AccessToken(row[5], row[7], user, int(row[6]))
            user.refresh_token = RefreshToken(row[9], row[11], user, int(row[10]))
            users.append(user)
        return users

class AuthCode:
    def __init__(self, code_id, code, user, time_added):
        self.id = code_id
        self.code = code
        self.user = user
        self.time_added = time_added

class RefreshToken:
    def __init__(self, token_id, token, user, time_added):
        self.id = token_id
        self.token = token
        self.time_added = time_added
        self.user = user

class AccessToken:
    def __init__(self, token_id, token, user, time_added):
        self.id = token_id
        self.token = token
        self.time_added = time_added
        self.user = user

    def expired(self):
        # expiry time is actually 3600 not 2500 but gotta be safe
        return self.time_added < current_time() - 2500 * 1000

class Play:
    def __init__(self, play_id, time_started, time_ended, user, track, device,
                 volume_percent, context=None, is_playing=False, progress_ms=-1):
        self.id = play_id
        self.time_started = time_started
        self.time_ended = time_ended
        self.user = user
        self.track = track
        self.device = device
        self.context = context
        self.is_playing = is_playing
        self.progress_ms = progress_ms
        self.volume_percent = volume_percent

class Pause:
    def __init__(self, pause_id, play, time_added):
        self.id = pause_id
        self.play = play
        self.time_added = time_added

class Resume:
    def __init__(self, resume_id, play, time_added):
        self.id = resume_id
        self.play = play
        self.time_added = time_added

class Seek:
    def __init__(self, seek_id, play, position, time_added):
        self.id = seek_id
        self.play = play
        self.position = position
        self.time_added = time_added

class Device:
    def __init__(self, device_id, name, device_type):
        self.id = device_id
        self.name = name
        self.type = device_type

class Context:
    def __init__(self, uri, context_type):
        self.uri = uri
        self.type = context_type

class Image:
    def __init__(self, image_id, url, width, height):
        self.id = image_id
        self.url = url
        self.width = width
        self.height = height
