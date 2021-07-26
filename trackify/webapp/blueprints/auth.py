import functools
from flask import (
    Blueprint, request, flash, g, redirect, session, render_template, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from trackify.utils import current_time, generate_id
from trackify.db.classes import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

def try_credentials(username, password):
    user = g.music_provider.get_user_by_username(username)
    if user and check_password_hash(user.password, password):
        return user
    return None

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if g.user:
        return redirect(url_for('home.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verified_password = request.form['verified_password']
        email = request.form['email']
        error = None

        if not password:
            error = 'password is required'
        elif not password == verified_password:
            error = 'passwords dont match'
        if not username:
            error = 'username is required'
        elif len(username) > 29:
            error = 'username too long'
        elif len(password) > 93:
            error = 'password too long'
        elif len(email) > 254:
            error = 'email too long'
        elif g.music_provider.get_user_by_username(username):
            error = 'username is not available'

        if not error:
            user = User(generate_id(), username, generate_password_hash(password),
                        email, current_time())
            g.music_provider.add_user(user)
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('home.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'username is required'
        elif not password:
            error = 'password is required'

        user = try_credentials(username, password)
        if not user:
            error = 'password/username incorrect'

        if not error:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('home.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
