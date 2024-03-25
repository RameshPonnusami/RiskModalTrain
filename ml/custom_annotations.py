from flask import render_template, request, jsonify, redirect, url_for, Response
from flask import session
from functools import wraps


def login_required(view_func) -> callable:
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or not session['username']:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)

    return decorated_function