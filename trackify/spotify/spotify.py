import requests
import json

from trackify.db.classes import RefreshToken, AccessToken
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
