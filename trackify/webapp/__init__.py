from flask import Flask, request, g, session
from flask_jwt_extended import JWTManager

from trackify.db.classes import MusicProvider, Request
from trackify.spotify.spotify import SpotifyClient
import config

def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        config.CONFIG_UPPERCASE
    )

    jwt = JWTManager(app)

    def terminate(e=None):
        if 'music_provider' in g:
            g.music_provider.close()
    app.teardown_appcontext(terminate)

    @app.before_request
    def before_request():
        if config.CONFIG['permanent_session']:
            session.permanent = True

        if not 'music_provider' in g:
            g.music_provider = MusicProvider(config.CONFIG['database_user'],
                                             config.CONFIG['database_password'],
                                             config.CONFIG['database'],
                                             config.CONFIG['database_host'])
        if not 'jwt' in g:
            g.jwt = jwt
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
            g.spotify_client = SpotifyClient(config.CONFIG['client_id'], config.CONFIG['client_secret'],
                                             config.CONFIG['redirect_uri'], config.CONFIG['scope'])

    from trackify.webapp.blueprints.home import bp as home_bp
    app.register_blueprint(home_bp)

    from trackify.webapp.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from trackify.webapp.blueprints.spotify import bp as spotify_bp
    app.register_blueprint(spotify_bp)

    from trackify.webapp.blueprints.static import bp as static_bp
    app.register_blueprint(static_bp)

    from trackify.webapp.blueprints.settings import bp as settings_bp
    app.register_blueprint(settings_bp)

    from trackify.webapp.blueprints.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app

web_application = create_app()
