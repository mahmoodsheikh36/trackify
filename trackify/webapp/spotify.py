import functools
from flask import Blueprint, render_template, g, redirect

from trackify.utils import uri_encode

bp = Blueprint('/spotify')

@requires_login
@bp.route('/spotify/auth', methods=('GET',))
def spotify_auth():
    spotify_auth_url = "https://accounts.spotify.com/authorize" +\
        "?response_type=code" +\
        '&client_id={}'.format(g.spotify_client.client_id) +\
        '&scope={}'.format(uri_encode(g.spotify_client.scope)) +\
        '&redirect_uri={}'.format(uri_encode(g.spotify_client.redirect_uri))
    return redirect(spotify_auth_url)

@bp.route('/spotify/callback', methods=('GET',))
