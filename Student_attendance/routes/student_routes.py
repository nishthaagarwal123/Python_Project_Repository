from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection
from utils import student_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_id = session['student_id']
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('auth.login_page'))
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        # Calculate attendance
        cursor.execute("""
            SELECT 
                COUNT(*) as total_classes,
                SUM(status = 'Present') as present,
                SUM(status = 'Absent') as absent
            FROM attendance
            WHERE student_id = %s
        """, (student_id,))
        att_stats = cursor.fetchone()
        
        total = att_stats['total_classes'] or 0
        present = att_stats['present'] or 0
        absent = att_stats['absent'] or 0
        percentage = round((present / total * 100), 2) if total > 0 else 0
        
        return render_template('student/dashboard.html', 
                               student=student, 
                               total=total, 
                               present=present, 
                               absent=absent, 
                               percentage=percentage)
    finally:
        cursor.close()
        conn.close()

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student_id = session['student_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        try:
            cursor.execute("""
                UPDATE students 
                SET name = %s, email = %s, phone = %s 
                WHERE student_id = %s
            """, (name, email, phone, student_id))
            conn.commit()
            session['name'] = name # Update session name
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            flash(f'Error updating profile: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('student.profile'))
    
    try:
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        return render_template('student/profile.html', student=student)
    finally:
        cursor.close()
        conn.close()

@student_bp.route('/attendance')
@student_required
def attendance():
    student_id = session['student_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get history
        cursor.execute("""
            SELECT attendance_date, status, updated_at
            FROM attendance
            WHERE student_id = %s
            ORDER BY attendance_date DESC
        """, (student_id,))
        history = cursor.fetchall()
        
        # Get stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_classes,
                SUM(status = 'Present') as present,
                SUM(status = 'Absent') as absent
            FROM attendance
            WHERE student_id = %s
        """, (student_id,))
        att_stats = cursor.fetchone()
        
        total = att_stats['total_classes'] or 0
        present = att_stats['present'] or 0
        absent = att_stats['absent'] or 0
        percentage = round((present / total * 100), 2) if total > 0 else 0
        
        return render_template('student/attendance.html', 
                               history=history,
                               total=total,
                               present=present,
                               absent=absent,
                               percentage=percentage)
    finally:
        cursor.close()
        conn.close()

@student_bp.route('/change_password', methods=['GET', 'POST'])
@student_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('student.change_password'))
            
        student_id = session['student_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT password FROM students WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()
            
            if student and check_password_hash(student['password'], current_password):
                hashed_pw = generate_password_hash(new_password)
                cursor.execute("UPDATE students SET password = %s WHERE student_id = %s", (hashed_pw, student_id))
                conn.commit()
                flash('Password changed successfully.', 'success')
            else:
                flash('Incorrect current password.', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('student.change_password'))
        
    return render_template('student/change_password.html')
