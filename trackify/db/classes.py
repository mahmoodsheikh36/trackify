from trackify import db
from trackify.utils import current_time, random_str

class Request:
    def __init__(flask_request):
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
    def __init__(self, user_id, username, password, email, time_added):
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.time_added = time_added

class Artist:
    def __init__(self, artist_id, name, albums):
        self.id = artist_id
        self.name = name

class Track:
    def __init__(self, name, album, duration_ms, popularity, preview_url, track_number,
                 explicit):
        self.name = name
        self.album = album
        self.duration_ms = duration_ms
        self.popularity = popularity
        self.preview_url = preview_url
        self.track_number = track_number
        self.explicit = explicit

class Album:
    def __init__(self, album_id, name, album_type, release_date, release_date_precision):
        self.id = album_id
        self.name = name
        self.type = album_type
        self.release_date = release_date
        self.release_date_precision = release_date_precision

class MusicProvider:
    def __init__(self, *args, **kwargs):
        self.db_provider = DBProvider(args, kwargs)
