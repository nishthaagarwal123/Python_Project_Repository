from functools import wraps
from flask import session, redirect, url_for, flash, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session.get('role') != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def faculty_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session.get('role') != 'faculty':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
