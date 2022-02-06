from flask import (
    Blueprint, render_template, g, redirect, url_for
)

from trackify.webapp.blueprints.spotify import top_users

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('', methods=('GET',))
def index():
    return render_template('home.html')
    #if not g.user:
    #    return redirect(url_for('auth.login'))
    if not g.db_data_provider.get_user_spotify_access_token(g.user):
        return render_template('index.html')
    #if not g.db_data_provider.user_has_plays(g.user):
    #    return render_template('index.html')
    #return redirect(url_for('spotify.data'))

@bp.route('index', methods=('GET',))
def index_page():
    return index()

@bp.route('home', methods=('GET',))
def home():
    return index()

@bp.route('top', methods=('GET',))
def top_users_alias():
    return top_users()
