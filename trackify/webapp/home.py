import functools
from flask import (
    Blueprint, render_template, g, redirect, url_for
)

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('', methods=('GET',))
def index():
    if not g.user:
        return redirect(url_for('auth.login'))
    if not g.music_provider.get_user_access_token(g.user):
        return render_template('index.html')
    return redirect(url_for('spotify.data'))

@bp.route('index', methods=('GET',))
def index_page():
    return index()

@bp.route('home', methods=('GET',))
def home():
    return index()
