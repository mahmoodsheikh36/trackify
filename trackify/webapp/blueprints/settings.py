from flask import (
    Blueprint, render_template, g, request
)
from trackify.webapp.blueprints.auth import login_required
from trackify.utils import str_to_bool

bp = Blueprint('settings', __name__, url_prefix='/settings/')

@bp.route('', methods=('GET', 'POST'))
@login_required
def settings():
    settings = g.db_data_provider.get_user_settings(g.user)
    if request.method == 'POST':
        for setting_id in settings:
            setting = settings[int(setting_id)]
            if setting.value_type == 'bool':
                if str(setting_id) in request.form:
                    new_value = request.form[str(setting_id)]
                    if len(new_value) > 9:
                        return '' # someone is trying to trick the webapp
                    setting.value = str_to_bool(request.form[str(setting_id)])
                else:
                    setting.value = False
        g.db_data_provider.update_user_settings(g.user, settings)
    return render_template('settings.html', settings=settings)
