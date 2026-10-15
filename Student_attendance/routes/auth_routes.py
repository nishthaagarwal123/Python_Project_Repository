from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    return render_template('auth/login.html')

@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        password = request.form.get('password')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return render_template('auth/student_login.html')

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()

            if student and check_password_hash(student['password'], password):
                session['student_id'] = student['student_id']
                session['role'] = 'student'
                session['name'] = student['name']
                return redirect(url_for('student.dashboard'))
            else:
                flash('Invalid Student ID or password.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('auth/student_login.html')

@auth_bp.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        password = request.form.get('password')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return render_template('auth/faculty_login.html')

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM faculty WHERE faculty_id = %s", (faculty_id,))
            faculty = cursor.fetchone()

            if faculty and check_password_hash(faculty['password'], password):
                session['faculty_id'] = faculty['faculty_id']
                session['role'] = 'faculty'
                session['name'] = faculty['name']
                return redirect(url_for('faculty.dashboard'))
            else:
                flash('Invalid Faculty ID or password.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('auth/faculty_login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login_page'))
