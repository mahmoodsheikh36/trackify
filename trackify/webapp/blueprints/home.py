from flask import (
    Blueprint, render_template, g, redirect, url_for
)

from trackify.webapp.blueprints.spotify import top_users

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('', methods=('GET',))
def index():
    if g.user:
        if not g.db_data_provider.get_user_spotify_access_token(g.user):
            return render_template('index.html')
    return render_template('home.html')

@bp.route('index', methods=('GET',))
def index_page():
    return index()

@bp.route('home', methods=('GET',))
def home():
    return index()

@bp.route('top', methods=('GET',))
def top_users_alias():
    return top_users()
