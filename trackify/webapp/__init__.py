from flask import Flask, request, g
import os

from trackify.db.classes import MusicProvider, Request

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # shouldnt be used in production!
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.before_request
    def before_request():
        if not 'music_provider' in g:
            g.music_provider = MusicProvider(app.config['DATABASE_USER'],
                                             app.config['DATABASE_PASSWD'],
                                             host=app.config['DATABASE_HOST'],
                                             database=app.config['DATABASE_NAME'])
            self.teardown_appcontext(g.music_provider.close)
        db_request = Request(request)
        g.music_provider.add_request(db_request)

    @app.after_request
    def add_header(r):
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    return app

web_application = create_app()
