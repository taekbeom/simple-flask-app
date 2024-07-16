from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user


# restricted for admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.has_role('admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# restricted for self and admin
def admin_or_self_required(f):
    @wraps(f)
    def decorated_function(user_id, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role.role_name != 'admin' and current_user.id != user_id:
            return redirect(url_for('index'))
        return f(user_id, *args, **kwargs)
    return decorated_function
