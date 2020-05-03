from flask import Flask, request, g
import os

from trackify.db.classes import MusicProvider, Request
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

    @app.before_request
    def before_request():
        if not 'music_provider' in g:
            g.music_provider = MusicProvider(Config.database_user,
                                             Config.database_password,
                                             Config.database,
                                             Config.database_host)
            app.teardown_appcontext(terminate)
        db_request = Request(request)
        g.music_provider.add_request(db_request)

    @app.after_request
    def add_header(r):
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    from trackify.webapp.home import bp as home_bp
    app.register_blueprint(home_bp)

    return app

web_application = create_app()
