import functools
from flask import Blueprint, render_template, g, redirect, request, url_for

from trackify.utils import uri_encode, generate_id, current_time
from trackify.webapp.auth import login_required
from trackify.db.classes import AuthCode

bp = Blueprint('spotify', __name__, url_prefix='/spotify')

@login_required
@bp.route('/auth', methods=('GET',))
def auth():
    spotify_auth_url = "https://accounts.spotify.com/authorize" +\
        "?response_type=code" +\
        '&client_id={}'.format(g.spotify_client.client_id) +\
        '&scope={}'.format(uri_encode(g.spotify_client.scope)) +\
        '&redirect_uri={}'.format(uri_encode(g.spotify_client.redirect_uri))
    return redirect(spotify_auth_url)

@login_required
@bp.route('/callback', methods=('GET',))
def callback():
    if g.music_provider.get_user_auth_code(g.user):
        return '' # in this case we know someone is trying to abuse the backend
    auth_code = AuthCode(generate_id(), request.args['code'],
                         g.user, current_time())
    g.music_provider.add_auth_code(auth_code)
    refresh_token, access_token = g.spotify_client.fetch_refresh_token(auth_code)
    if access_token and refresh_token:
        g.music_provider.add_refresh_token(refresh_token)
        g.music_provider.add_access_token(access_token)
    return redirect(url_for('home.home'))

@login_required
@bp.route('/data', methods=('GET',))
def data():
    if not g.music_provider.get_user_auth_code(g.user):
        return ''
    plays, tracks = g.music_provider.get_user_music(g.user)
    for play in plays.values():
        track = tracks[play.track.id]
        if hasattr(track, 'listened_ms'):
            track.listened_ms += play.listened_ms()
        else:
            track.listened_ms = play.listened_ms()
    return render_template('data.html', tracks=tracks.values())
