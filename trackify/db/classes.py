import json

from trackify.db.db import DBProvider
from trackify.utils import current_time, generate_id, str_to_bool

class Request:
    def __init__(self, flask_request, user):
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
        self.user = user

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
        self.settings = Settings()

class Artist:
    def __init__(self, artist_id, name, albums):
        self.id = artist_id
        if not self.id:
            self.id = generate_id(24)
        self.name = name
        self.albums = albums

class Track:
    def __init__(self, track_id, name, album, artists, duration_ms, popularity,
                 preview_url, track_number, explicit):
        self.id = track_id
        if not self.id:
            self.id = generate_id()
        self.name = name
        self.album = album
        self.artists = artists
        self.duration_ms = duration_ms
        self.popularity = popularity
        self.preview_url = preview_url
        self.track_number = track_number
        self.explicit = explicit

class Album:
    def __init__(self, album_id, name, tracks, artists, images, album_type,
                 release_date, release_date_precision):
        self.id = album_id
        if not self.id:
            self.id = generate_id(24)
        self.name = name
        self.type = album_type
        self.artists = artists
        self.tracks = tracks
        self.images = images
        self.release_date = release_date
        self.release_date_precision = release_date_precision

    def smallest_image(self):
        smallest = self.images[0]
        for idx, image in enumerate(self.images[1:]):
            if image.width < smallest.width:
                smallest = image
        return smallest

    def biggest_image(self):
        biggest = self.images[0]
        for idx, image in enumerate(self.images[1:]):
            if image.width > biggest.width:
                biggest = image
        return biggest

    def add_image(self, new_image):
        if not self.images:
            self.images.append(new_image)
        else:
            found_idx = False
            for idx, image in enumerate(self.images):
                if new_image.width < image.width:
                    self.images.insert(idx, new_image)
                    found_idx = True
                    break
            if not found_idx:
                self.images.append(new_image)

    def mid_sized_image(self):
        return self.images[len(self.images) // 2]

class MusicProvider:
    def __init__(self, *args, **kwargs):
        self.db_provider = DBProvider(*args, **kwargs)

    def close(self):
        self.db_provider.close()

    def commit(self):
        self.db_provider.commit()

    def new_conn(self):
        self.db_provider.new_conn()

    def get_user_by_username(self, username):
        user_row = self.db_provider.get_user_by_username(username)
        if user_row:
            return User(user_row['id'], user_row['username'], user_row['password'],
                        user_row['email'], user_row['time_added'])
        return None

    def add_user(self, user):
        self.db_provider.add_user(user.id, user.username, user.password, user.email,
                                  user.time_added)
        self.commit()

    def add_request(self, request):
        user_id = None
        if request.user:
            user_id = request.user.id
        self.db_provider.add_request(request.id, request.time_added, request.ip,
                                     request.url, request.headers, request.data,
                                     request.form, request.referrer,
                                     request.access_route, user_id)
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
            return User(user_row['id'], user_row['username'], user_row['password'],
                        user_row['email'], user_row['time_added'])
        return None

    def get_user_auth_code(self, user):
        code_row = self.db_provider.get_user_auth_code(user.id)
        if code_row:
            return AuthCode(code_row['id'], code_row['code'], user,
                            code_row['time_added'])
        return None

    def get_user_access_token(self, user):
        token_row = self.db_provider.get_user_access_token(user.id)
        if token_row:
            return AccessToken(token_row['id'], token_row['token'], user,
                               token_row['time_added'])
        return None

    def get_user_refresh_token(self, user):
        token_row = self.db_provider.get_user_refresh_token(user.id)
        if token_row:
            return RefreshToken(token_row['id'], token_row['token'], user,
                                token_row['time_added'])
        return None

    def get_users(self):
        user_rows = self.db_provider.get_users()
        users = []
        for user_row in user_rows:
            user = User(user_row['id'], user_row['username'], user_row['password'],
                        user_row['email'], user_row['time_added'])
            users.append(user)
        return users

    def get_user_access_token(self, user):
        row = self.db_provider.get_user_access_token(user.id)
        if row:
            return AccessToken(row['id'], row['token'], user, row['time_added'])
        return None

    def get_user_refresh_token(self, user):
        row = self.db_provider.get_user_refresh_token(user.id)
        return RefreshToken(row['id'], row['token'], user, row['time_added'])

    def get_users_with_tokens(self):
        rows = self.db_provider.get_users_with_tokens()
        users = []
        for row in rows:
            user = User(row['id'], row['username'], row['password'], row['email'],
                        row['time_added'])
            user.access_token = AccessToken(row['id'], row['token'], user,
                                            row['time_added'])
            user.refresh_token = RefreshToken(row['id'], row['token'], user,
                                              row['time_added'])
            users.append(user)
        return users

    def get_user_data(self, user, from_time=0, to_time=9999999999999):
        db_rows = self.db_provider.get_user_data(user.id, from_time, to_time)

        tracks = {}
        albums = {}
        artists = {}
        plays = {}
        album_images = {}

        seeks = {}
        pauses = {}
        resumes = {}

        for row in db_rows:
            if row['artist_id'] in artists:
                artist = artists[row['artist_id']]
            else:
                artist = Artist(row['artist_id'], row['artist_name'], [])
                artists[artist.id] = artist

            if row['album_id'] in albums:
                album = albums[row['album_id']]
            else:
                album = Album(row['album_id'], row['album_name'], [], [artist], [],
                              row['album_type'], row['album_release_date'],
                              row['album_release_date_precision'])
                albums[album.id] = album
                artist.albums.append(album)

            if row['track_id'] in tracks:
                track = tracks[row['track_id']]
            else:
                track = Track(row['track_id'], row['track_name'], album, [artist],
                              row['track_duration_ms'], row['track_popularity'],
                              row['track_preview_url'], row['track_number'],
                              row['track_explicit'])
                album.tracks.append(track)
                tracks[track.id] = track

            if not row['play_id'] in plays:
                play = Play(row['play_id'], row['play_time_started'],
                            row['play_time_ended'], [], [], [],
                            user, track, None, row['play_volume_percent'])
                plays[play.id] = play
            else:
                play = plays[row['play_id']]

            if not row['seek_id'] in seeks and row['seek_id']:
                seek = Seek(row['seek_id'], play, row['seek_position'],
                            row['seek_time_added'])
                play.seeks.append(seek)
                seeks[seek.id] = seek
            if not row['pause_id'] in pauses and row['pause_id']:
                pause = Pause(row['pause_id'], play, row['pause_time_added'])
                play.pauses.append(pause)
                pauses[pause.id] = pause
            if not row['resume_id'] in resumes and row['resume_id']:
                resume = Resume(row['resume_id'], play, row['resume_time_added'])
                play.resumes.append(resume)
                resumes[resume.id] = resume

            if row['album_image_id'] and not row['album_image_id'] in album_images:
                image = Image(row['album_image_id'], row['album_image_url'],
                              row['album_image_width'], row['album_image_height'])
                album_images[row['album_image_id']] = image
                albums[row['album_id']].add_image(image)

        return artists, albums, tracks, plays

    def get_all_users_data(self, from_time=0, to_time=9999999999999):
        begin = current_time()
        db_rows = self.db_provider.get_all_users_data(from_time, to_time)

        tracks = {}
        albums = {}
        artists = {}
        plays = {}
        users = {}

        seeks = {}
        pauses = {}
        resumes = {}

        for row in db_rows:
            if row['user_id'] in users:
                user = users[row['user_id']]
            else:
                user = User(row['user_id'], row['user_username'], None, None,
                            row['user_time_added'], plays=[])
                user.settings.append_all([setting for setting in
                                          self.get_user_settings(user).values()])
                users[user.id] = user

            if row['artist_id'] in artists:
                artist = artists[row['artist_id']]
            else:
                artist = Artist(row['artist_id'], row['artist_name'], [])
                artists[artist.id] = artist

            if row['album_id'] in albums:
                album = albums[row['album_id']]
            else:
                image = Image(row['album_image_id'], row['album_image_url'],
                              row['album_image_width'], row['album_image_height'])
                album = Album(row['album_id'], row['album_name'], [], [artist], [image],
                              row['album_type'], row['album_release_date'],
                              row['album_release_date_precision'])
                albums[album.id] = album
                artist.albums.append(album)

            if row['track_id'] in tracks:
                track = tracks[row['track_id']]
            else:
                track = Track(row['track_id'], row['track_name'], album, [artist],
                              row['track_duration_ms'], row['track_popularity'],
                              row['track_preview_url'], row['track_number'],
                              row['track_explicit'])
                album.tracks.append(track)
                tracks[track.id] = track

            if not row['play_id'] in plays:
                play = Play(row['play_id'], row['play_time_started'],
                            row['play_time_ended'], [], [], [],
                            user, track, None, row['play_volume_percent'])
                plays[play.id] = play
                user.plays.append(play)
            else:
                play = plays[row['play_id']]

            if not row['seek_id'] in seeks and row['seek_id']:
                seek = Seek(row['seek_id'], play, row['seek_position'],
                            row['seek_time_added'])
                play.seeks.append(seek)
                seeks[seek.id] = seek
            if not row['pause_id'] in pauses and row['pause_id']:
                pause = Pause(row['pause_id'], play, row['pause_time_added'])
                play.pauses.append(pause)
                pauses[pause.id] = pause
            if not row['resume_id'] in resumes and row['resume_id']:
                resume = Resume(row['resume_id'], play, row['resume_time_added'])
                play.resumes.append(resume)
                resumes[resume.id] = resume

        return users, artists, albums, tracks, plays

    def add_album(self, album):
        self.db_provider.add_album(album.id, album.name, album.type, album.release_date,
                                   album.release_date_precision)
        for artist in album.artists:
            if not self.db_provider.get_artist(artist.id):
                self.db_provider.add_artist(artist.id, artist.name)
            self.db_provider.add_album_artist(generate_id(), album.id, artist.id)
        for image in album.images:
            self.db_provider.add_album_image(image.id, image.url, album.id, image.width,
                                             image.height)

    def add_track(self, track):
        if not self.db_provider.get_album(track.album.id):
            self.add_album(track.album)
        self.db_provider.add_track(track.id, track.name, track.duration_ms,
                                   track.popularity, track.preview_url,
                                   track.track_number, track.explicit, track.album.id)
        for artist in track.artists:
            if not self.db_provider.get_artist(artist.id):
                self.db_provider.add_artist(artist.id, artist.name)
            self.db_provider.add_track_artist(generate_id(), track.id, artist.id)
        
    # NOTE: doesnt handle adding resumes and pauses from Play object
    def add_play(self, play):
        if not self.db_provider.get_track(play.track.id):
            self.add_track(play.track)
        if not self.db_provider.get_album(play.track.album.id):
            self.add_album(play.track.album)
        if play.context:
            if not self.db_provider.get_context(play.context.uri):
                self.db_provider.add_context(play.context.uri, play.context.type)
        if not self.db_provider.get_device(play.device.id):
            self.db_provider.add_device(play.device.id, play.device.name,
                                        play.device.type)
        self.db_provider.add_play(play.id, play.time_started, play.time_ended,
                                  play.volume_percent, play.user.id, play.track.id,
                                  play.device.id,
                                  play.context.uri if play.context else None)
        self.commit()

    def get_track(self, track_id):
        row = self.db_provider.get_track(track_id)
        if not row:
            return None
        return Track(row['id'], row['track_name'], None, [], row['duration_ms'],
                     row['popularity'], row['preview_url'], row['track_number'],
                     row['explicit'])

    def get_last_user_play(self, user):
        row = self.db_provider.get_last_user_play(user.id)
        if row:
            track = self.get_track(row['track_id'])
            return Play(row['id'], row['time_added'], row['time_ended'], None, None, None,
                        user, track, None, row['volume_percent'])
        return None

    def update_play_time_ended(self, play):
        self.db_provider.update_play_time_ended(play.id, play.time_ended)
        self.commit()

    def add_pause(self, pause):
        self.db_provider.add_pause(pause.id, pause.time_added, pause.play.id)
        self.commit()

    def add_resume(self, resume):
        self.db_provider.add_resume(resume.id, resume.time_added, resume.play.id)
        self.commit()

    def add_seek(self, seek):
        self.db_provider.add_seek(seek.id, seek.time_added, seek.position, seek.play.id)
        self.commit()

    def user_has_plays(self, user):
        return self.db_provider.user_has_plays(user.id)

    def get_user_settings(self, user):
        user_setting_rows = self.db_provider.get_user_settings(user.id)
        setting_rows = self.db_provider.get_settings()
        user_settings = {}
        for setting_row in setting_rows:
            user_setting_row = None
            for tmp_user_setting_row in user_setting_rows:
                if tmp_user_setting_row['setting_id'] == setting_row['id']:
                    user_setting_row = tmp_user_setting_row
            setting_value = setting_row['default_value']
            if user_setting_row:
                setting_value = user_setting_row['setting_value']
            if setting_row['value_type'] == 'bool':
                setting_value = str_to_bool(setting_value)
            setting = Setting(setting_row['id'], setting_row['setting_name'],
                              setting_row['description'], setting_value,
                              setting_row['value_type'])
            user_settings[setting_row['id']] = setting
        return user_settings

    def update_user_settings(self, user, settings):
        for setting_id in settings:
            setting = settings[setting_id]
            value = setting.value
            if setting.value_type == 'bool':
                value = str(value)
            if self.db_provider.get_user_setting(user.id, setting.id):
                self.db_provider.update_user_setting(setting.id, user.id, value)
            else:
                self.db_provider.add_user_setting(setting.id, user.id, value)
        self.commit()

    def get_user_track_plays(self, user, track, from_time=0, to_time=9999999999999):
        rows = self.db_provider.get_user_track_plays(user.id, track.id, from_time, to_time)
        plays = []
        for row in rows:
            plays.append(Play(row['id'], row['time_added'], row['time_ended'], None, None, None,
                              user, None, None, row['volume_percent']))
        return plays

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
    def __init__(self, play_id, time_started, time_ended, pauses, resumes, seeks, user,
                 track, device, volume_percent, context=None, is_playing=False,
                 progress_ms=-1):
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
        self.pauses = pauses
        self.resumes = resumes
        self.seeks = seeks

    def has_same_track_as(self, other_play):
        return self.track.id == other_play.track.id

    def listened_ms(self, from_time=None, to_time=None):
        if self.time_ended == -1:
            return 0
        if abs(len(self.pauses) - len(self.resumes)) > 1:
            return 0
        if from_time is None:
            from_time = self.time_started
        elif from_time > self.time_ended:
            return 0
        if to_time is None:
            to_time = self.time_ended
        elif to_time < self.time_started:
            return 0
        if from_time < self.time_started:
            from_time = self.time_started
        if to_time > self.time_ended:
            to_time = self.time_ended
        milliseconds = to_time - from_time
        for i in range(len(self.resumes)):
            pause = self.pauses[i]
            resume = self.resumes[i]
            time_paused = pause.time_added
            time_resumed = resume.time_added
            if time_paused > to_time:
                continue
            if time_resumed < from_time:
                continue
            if time_paused < from_time:
                time_paused = from_time
            if time_resumed > to_time:
                time_resumed = to_time
            milliseconds -= time_resumed - time_paused
        if len(self.pauses) > len(self.resumes):
            time_paused = self.pauses[-1].time_added
            if time_paused < to_time:
                if time_paused < from_time:
                    time_paused = from_time
                milliseconds -= to_time - time_paused
        return milliseconds

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

class Setting:
    def __init__(self, setting_id, name, description, value, value_type):
        self.id = setting_id
        self.name = name
        self.description = description
        self.value = value
        self.value_type = value_type

class Settings:
    def __init__(self, settings=[]):
        self.settings = settings

    def append(self, setting):
        self.settings.append(setting)

    def append_all(self, settings):
        for setting in settings:
            self.settings.append(setting)

    def get_by_name(self, setting_name):
        for setting in self.settings:
            if setting.name == setting_name:
                return setting
        return None
