from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection
from utils import faculty_required
import mysql.connector

faculty_bp = Blueprint('faculty', __name__)

@faculty_bp.route('/dashboard')
@faculty_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Total students
        cursor.execute("SELECT COUNT(*) as count FROM students")
        total_students = cursor.fetchone()['count']
        
        # Today's attendance summary
        cursor.execute("""
            SELECT 
                SUM(status = 'Present') as present,
                SUM(status = 'Absent') as absent
            FROM attendance
            WHERE attendance_date = CURRENT_DATE()
        """)
        today_att = cursor.fetchone()
        today_present = today_att['present'] or 0
        today_absent = today_att['absent'] or 0
        
        # Overall records
        cursor.execute("SELECT COUNT(*) as count FROM attendance")
        total_records = cursor.fetchone()['count']
        
        return render_template('faculty/dashboard.html',
                               total_students=total_students,
                               today_present=today_present,
                               today_absent=today_absent,
                               total_records=total_records)
    finally:
        cursor.close()
        conn.close()

@faculty_bp.route('/students', methods=['GET'])
@faculty_required
def students():
    search = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if search:
            cursor.execute("SELECT * FROM students WHERE name LIKE %s OR student_id = %s", (f"%{search}%", search if search.isdigit() else -1))
        else:
            cursor.execute("SELECT * FROM students")
        all_students = cursor.fetchall()
        return render_template('faculty/students.html', students=all_students, search=search)
    finally:
        cursor.close()
        conn.close()

@faculty_bp.route('/students/add', methods=['GET', 'POST'])
@faculty_required
def add_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        course = request.form.get('course')
        
        if not student_id:
            flash('Student ID is required.', 'danger')
            return redirect(url_for('faculty.add_student'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('faculty.add_student'))
            
        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO students (student_id, name, email, password, phone, course)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, name, email, hashed_pw, phone, course))
            conn.commit()
            flash('Student added successfully.', 'success')
            return redirect(url_for('faculty.students'))
        except mysql.connector.IntegrityError as e:
            flash(f'Database error (Duplicate ID or Email?): {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('faculty/add_student.html')

@faculty_bp.route('/students/edit/<student_id>', methods=['GET', 'POST'])
@faculty_required
def edit_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            course = request.form.get('course')
            
            cursor.execute("""
                UPDATE students
                SET name=%s, email=%s, phone=%s, course=%s
                WHERE student_id=%s
            """, (name, email, phone, course, student_id))
            conn.commit()
            flash('Student updated successfully.', 'success')
            return redirect(url_for('faculty.students'))
            
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            flash('Student not found.', 'danger')
            return redirect(url_for('faculty.students'))
        return render_template('faculty/edit_student.html', student=student)
    except mysql.connector.IntegrityError as e:
        flash(f'Database error: {e}', 'danger')
        return redirect(url_for('faculty.edit_student', student_id=student_id))
    finally:
        cursor.close()
        conn.close()

@faculty_bp.route('/students/delete/<student_id>', methods=['POST'])
@faculty_required
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        flash('Student deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting student: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('faculty.students'))

@faculty_bp.route('/change_password', methods=['GET', 'POST'])
@faculty_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('faculty.change_password'))
            
        faculty_id = session['faculty_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT password FROM faculty WHERE faculty_id = %s", (faculty_id,))
            faculty = cursor.fetchone()
            
            if faculty and check_password_hash(faculty['password'], current_password):
                hashed_pw = generate_password_hash(new_password)
                cursor.execute("UPDATE faculty SET password = %s WHERE faculty_id = %s", (hashed_pw, faculty_id))
                conn.commit()
                flash('Password changed successfully.', 'success')
            else:
                flash('Incorrect current password.', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('faculty.change_password'))
        
    return render_template('faculty/change_password.html')
