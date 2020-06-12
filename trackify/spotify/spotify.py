import requests
import requests.exceptions
import json

from trackify.db.classes import (
    RefreshToken, AccessToken, Device, Artist, Play, Image, Context, Album, Track
)
from trackify.utils import generate_id, current_time

class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri, scope):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

    def fetch_refresh_token(self, auth_code):
        r = requests.post('https://accounts.spotify.com/api/token',
                          data = {
                              'grant_type': 'authorization_code',
                              'code': auth_code.code,
                              'redirect_uri': self.redirect_uri,
                              'client_id': self.client_id,
                              'client_secret': self.client_secret
                          })
        if r.status_code != 200:
            return None, None
        r_json = json.loads(r.text)
        access_token = AccessToken(generate_id(), r_json['access_token'], auth_code.user,
                                   current_time())
        refresh_token = RefreshToken(generate_id(), r_json['refresh_token'],
                                     auth_code.user, current_time())
        return refresh_token, access_token

    def fetch_access_token(self, refresh_token):
        r = requests.post('https://accounts.spotify.com/api/token',
                          data = {
                              'grant_type': 'refresh_token',
                              'refresh_token': refresh_token.token,
                              'client_id': self.client_id,
                              'client_secret': self.client_secret
                          })
        if r.status_code != 200:
            return None
        r_json = json.loads(r.text)
        access_token = AccessToken(generate_id(), r_json['access_token'],
                                   refresh_token.user, current_time())
        return access_token

    def get_current_play(self, access_token):
        try:
            r = requests.get('https://api.spotify.com/v1/me/player',
                             headers = {
                                 'Authorization': 'Bearer {}'.format(access_token.token)
                             })
        except requests.exceptions.RequestException as e:
            return None, None
        if r.status_code == 429: # we hit rate limit
            if 'Retry-After' in r.headers:
                if r.headers['Retry-After']:
                    return None, int(r.headers['Retry-After'])
            return None, None
        if r.text == '':
            return None, None

        try:
            r_json = json.loads(r.text)
        except:
            return None, None

        if not 'is_playing' in r_json or not r_json['item']\
           or not 'id' in r_json['item']['album'] or not r_json['item']['album']['id']\
           or not r_json['device']['id']:
            return None, None

        device = Device(r_json['device']['id'], r_json['device']['name'],
                        r_json['device']['type'])

        context = None
        if r_json['context']:
            context = Context(r_json['context']['uri'], r_json['context']['type'])

        track_json = r_json['item']
        album_json = r_json['item']['album']

        album_images = []
        for image_json in r_json['item']['album']['images']:
            image = Image(generate_id(), image_json['url'], image_json['width'],
                          image_json['height'])
            album_images.append(image)

        album_artists = []
        for artist_json in album_json['artists']:
            album_artists.append(Artist(artist_json['id'], artist_json['name'], None))

        album = Album(album_json['id'], album_json['name'], None, album_artists,
                      album_images, album_json['type'], album_json['release_date'],
                      album_json['release_date_precision'])

        track_artists = []
        for artist_json in track_json['artists']:
            track_artists.append(Artist(artist_json['id'], artist_json['name'], None))

        track = Track(track_json['id'], track_json['name'], album, track_artists,
                      track_json['duration_ms'], track_json['popularity'],
                      track_json['preview_url'], track_json['track_number'],
                      track_json['explicit'])
        play = Play(generate_id(), current_time(), -1, None, None, None,
                    access_token.user,
                    track, device, r_json['device']['volume_percent'],
                    context, r_json['is_playing'],
                    int(r_json['progress_ms']))

        return play, None
