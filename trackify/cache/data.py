import redis
import json

from trackify.db.classes import User, Setting, Artist, Image, Album, Track

class CacheDataProvider:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def get(self, key):
        return self.redis.get(key)

    def set(self, key, val):
        return self.redis.set(key, val)

    def delete(self, key):
        val = self.redis.get(key)
        delete(key)
        return val

    def set_top_users(self, hrs_limit, top_users_data):
        data_to_cache = [{
            'id': user.id,
            'username': user.username,
            'settings': [{
                'id': setting.id,
                'name': setting.name,
                'value': setting.value,
            } for setting in user.settings.settings],
            'top_track': {
                'id': user.top_track.id,
                'name': user.top_track.name,
                'artists': [{
                    'id': artist.id,
                    'name': artist.name
                } for artist in user.top_track.artists],
                'album': {
                    'id': user.top_track.album.id,
                    'name': user.top_track.album.name,
                    'artists': [{
                        'id': artist.id,
                        'name': artist.name
                    } for artist in user.top_track.album.artists],
                    'images': [{
                        'id': image.id,
                        'url': image.url,
                        'width': image.width,
                        'height': image.height,
                    } for image in user.top_track.album.images]
                },
            },
            'listened_ms': user.listened_ms
        } for user in top_users_data]

        self.set(hrs_limit, json.dumps(data_to_cache))

    def get_top_users(self, hrs_limit):
        top_users_data = json.loads(self.get(hrs_limit))
        if top_users_data is None:
            return None
        top_users = []
        for entry in top_users_data:
            user = User(entry['id'], entry['username'], None, None, None)
            album_artists = []
            album_images = []
            track_artists = []
            for user_setting_entry in entry['settings']:
                user.settings.append(Setting(user_setting_entry['id'], user_setting_entry['name'],
                                            None, user_setting_entry['value'], None))
            for album_artist_entry in entry['top_track']['album']['artists']:
                album_artists.append(Artist(album_artist_entry['id'], album_artist_entry['name'], []))
            for album_image_entry in entry['top_track']['album']['images']:
                album_images.append(Image(album_image_entry['id'], album_image_entry['url'],
                                        album_image_entry['width'], album_image_entry['height']))
            for track_artist_entry in entry['top_track']['artists']:
                track_artists.append(Artist(track_artist_entry['id'], track_artist_entry['name'], []))
            album = Album(entry['top_track']['album']['id'], entry['top_track']['album']['name'],
                        None, album_artists, album_images, None, None, None)
            user.top_track = Track(entry['top_track']['id'], entry['top_track']['name'],
                                album, track_artists, None, None, None, None, None)
            user.listened_ms = entry['listened_ms']
            top_users.append(user)
        return top_users

    def set_artist_discogs_data(self, artist_name, artist_data):
        self.set(artist_name, json.dumps(artist_data))

    def get_artist_discogs_data(self, artist_name):
        try:
            return json.loads(self.get(artist_name))
        except TypeError: # incase redis returns None
            return None
