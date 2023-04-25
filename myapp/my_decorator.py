from functools import wraps
from flask import current_app, redirect, url_for, abort, flash
from flask_login import current_user

def logout_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('Tienda.index'))
        return func(*args, **kwargs)
    return decorated_view

def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if not any(r.name in roles for r in current_user.roles):
                flash('No tienes permiso para acceder a esta página', 'error')
                return redirect(url_for('Productos.get_Productos'))
            return func(*args, **kwargs)
        return decorated_view
    return decorator