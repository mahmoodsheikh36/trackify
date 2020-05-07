import functools
from flask import (
    Blueprint, render_template, g
)

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('', methods=('GET',))
def index():
    return render_template('index.html')

@bp.route('index', methods=('GET',))
def index_page():
    return index()

@bp.route('home', methods=('GET',))
def home():
    return index()

@bp.route('mus', methods=('GET',))
def mus():
    tracks = g.music_provider.get_tracks()
    print(tracks)
    return 'hello<br>there'
