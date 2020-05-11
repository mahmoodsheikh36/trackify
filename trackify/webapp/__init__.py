from flask import Flask, request, g, session
import os

from trackify.db.classes import MusicProvider, Request
from trackify.config import Config
from trackify.spotify.spotify import SpotifyClient
from trackify.config import Config

def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=Config.secret_key, # shouldnt be used in production!
    )

    def terminate(e=None):
        if 'music_provider' in g:
            g.music_provider.close()
    app.teardown_appcontext(terminate)

    @app.before_request
    def before_request():
        if not 'music_provider' in g:
            g.music_provider = MusicProvider(Config.database_user,
                                             Config.database_password,
                                             Config.database,
                                             Config.database_host)
        db_request = Request(request, None)

        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            # here g.user could be None if no user with that id was in database
            g.user = g.music_provider.get_user(user_id)

        db_request.user = g.user
        g.music_provider.add_request(db_request)

        if not 'spotify_client' in g:
            g.spotify_client = SpotifyClient(Config.client_id, Config.client_secret,
                                             Config.redirect_uri, Config.scope)

    @app.after_request
    def add_header(r):
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    from trackify.webapp.home import bp as home_bp
    app.register_blueprint(home_bp)

    from trackify.webapp.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from trackify.webapp.spotify import bp as spotify_bp
    app.register_blueprint(spotify_bp)

    from trackify.webapp.static import bp as static_bp
    app.register_blueprint(static_bp)

    return app

web_application = create_app()
