from flask import Flask, request, g, session
from flask_jwt_extended import JWTManager

from trackify.db.classes import MusicProvider, Request
from trackify.spotify.spotify import SpotifyClient
import config

def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=config.secret_key,
        JWT_SECRET_KEY=config.jwt_secret_key,
        JWT_ACCESS_TOKEN_EXPIRES=config.jwt_access_token_expires
    )

    jwt = JWTManager(app)

    def terminate(e=None):
        if 'music_provider' in g:
            g.music_provider.close()
    app.teardown_appcontext(terminate)

    @app.before_request
    def before_request():
        if not 'music_provider' in g:
            g.music_provider = MusicProvider(config.database_user,
                                             config.database_password,
                                             config.database,
                                             config.database_host)
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
            g.spotify_client = SpotifyClient(config.client_id, config.client_secret,
                                             config.redirect_uri, config.scope)

    from trackify.webapp.home import bp as home_bp
    app.register_blueprint(home_bp)

    from trackify.webapp.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from trackify.webapp.spotify import bp as spotify_bp
    app.register_blueprint(spotify_bp)

    from trackify.webapp.static import bp as static_bp
    app.register_blueprint(static_bp)

    from trackify.webapp.settings import bp as settings_bp
    app.register_blueprint(settings_bp)

    from trackify.webapp.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app

web_application = create_app()
