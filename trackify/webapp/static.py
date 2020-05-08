from flask import (
    Blueprint, send_from_directory
)
bp = Blueprint('static', __name__, url_prefix='/static')

@bp.route('/css/<path:path>')
def css(path):
    return send_from_directory('static/css', path)

@bp.route('/js/<path:path>')
def js(path):
    return send_from_directory('static/js', path)

# @bp.route('/<path:path>')
# def static_file_full_path(path):
#     return send_from_directory('static', path)
