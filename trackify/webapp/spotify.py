import functools
from flask import Blueprint, render_template, g, redirect, request, url_for

from trackify.utils import uri_encode, generate_id, current_time, get_largest_elements
from trackify.webapp.auth import login_required
from trackify.db.classes import AuthCode

bp = Blueprint('spotify', __name__, url_prefix='/spotify')

@bp.route('/auth', methods=('GET',))
@login_required
def auth():
    spotify_auth_url = "https://accounts.spotify.com/authorize" +\
        "?response_type=code" +\
        '&client_id={}'.format(g.spotify_client.client_id) +\
        '&scope={}'.format(uri_encode(g.spotify_client.scope)) +\
        '&redirect_uri={}'.format(uri_encode(g.spotify_client.redirect_uri))
    return redirect(spotify_auth_url)

@bp.route('/callback', methods=('GET',))
@login_required
def callback():
    auth_code = AuthCode(generate_id(), request.args['code'],
                         g.user, current_time())
    g.music_provider.add_auth_code(auth_code)
    refresh_token, access_token = g.spotify_client.fetch_refresh_token(auth_code)
    if access_token and refresh_token:
        g.music_provider.add_refresh_token(refresh_token)
        g.music_provider.add_access_token(access_token)
    return redirect(url_for('home.index'))

@bp.route('/data', methods=('GET',))
@login_required
def data():
    artists, albums, tracks, plays = g.music_provider.get_user_data(g.user)
    for play in plays.values():
        track = tracks[play.track.id]
        if hasattr(track, 'listened_ms'):
            track.listened_ms += play.listened_ms()
        else:
            track.listened_ms = play.listened_ms()

    for album in albums.values():
        for track in album.tracks:
            if hasattr(album, 'listened_ms'):
                album.listened_ms += track.listened_ms
            else:
                album.listened_ms = track.listened_ms

    for artist in artists.values():
        print('{} {}'.format(artist.id, len(artist.albums)))
        for album in artist.albums:
            if hasattr(album, 'listened_ms'):
                if hasattr(artist, 'listened_ms'):
                    artist.listened_ms += album.listened_ms
                else:
                    artist.listened_ms = album.listened_ms

    LIMIT = 100

    def compare(music_obj1, music_obj2):
        if not hasattr(music_obj1, 'listened_ms'):
            return False
        if not hasattr(music_obj2, 'listened_ms'):
            return True
        return music_obj1.listened_ms > music_obj2.listened_ms

    top_tracks = get_largest_elements(list(tracks.values()), LIMIT, compare)
    top_albums = get_largest_elements(list(albums.values()), LIMIT, compare)
    top_artists = get_largest_elements(list(artists.values()), LIMIT, compare)
    
    return render_template('data.html',
                           top_tracks=top_tracks,
                           top_albums=top_albums,
                           top_artists=top_artists)
