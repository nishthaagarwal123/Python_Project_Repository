from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from utils import faculty_required
from datetime import datetime
import mysql.connector

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['GET', 'POST'])
@faculty_required
def mark():
    date_str = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'POST':
            date_to_mark = request.form.get('date')
            faculty_id = session['faculty_id']
            
            # Fetch all student ids from the form
            cursor.execute("SELECT student_id FROM students")
            all_students = cursor.fetchall()
            
            success_count = 0
            for student in all_students:
                s_id = str(student['student_id'])
                status = request.form.get(f'status_{s_id}')
                if status:
                    try:
                        cursor.execute("""
                            INSERT INTO attendance (student_id, attendance_date, status, marked_by)
                            VALUES (%s, %s, %s, %s)
                        """, (s_id, date_to_mark, status, faculty_id))
                        success_count += 1
                    except mysql.connector.IntegrityError:
                        # Already exists, skip or show message
                        pass
            
            conn.commit()
            if success_count > 0:
                flash(f'Successfully marked attendance for {success_count} students.', 'success')
            else:
                flash('No new attendance records added. (Perhaps they were already marked?)', 'warning')
            return redirect(url_for('attendance.mark', date=date_to_mark))

        # For GET, retrieve students and existing attendance for the date
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        
        cursor.execute("""
            SELECT student_id, status FROM attendance WHERE attendance_date = %s
        """, (date_str,))
        existing_att = {row['student_id']: row['status'] for row in cursor.fetchall()}
        
        return render_template('faculty/attendance.html', students=students, date=date_str, existing_att=existing_att)
    finally:
        cursor.close()
        conn.close()

@attendance_bp.route('/update', methods=['POST'])
@faculty_required
def update():
    date_to_update = request.form.get('date')
    student_id = request.form.get('student_id')
    new_status = request.form.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE attendance 
            SET status = %s, marked_by = %s 
            WHERE student_id = %s AND attendance_date = %s
        """, (new_status, session['faculty_id'], student_id, date_to_update))
        conn.commit()
        flash('Attendance updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating attendance: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('attendance.mark', date=date_to_update))

@attendance_bp.route('/report', methods=['GET'])
@faculty_required
def report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                s.student_id,
                s.name,
                COUNT(a.attendance_id) as total,
                SUM(a.status = 'Present') as present,
                SUM(a.status = 'Absent') as absent
            FROM students s
            LEFT JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name
        """)
        report_data = cursor.fetchall()
        
        for row in report_data:
            t = row['total'] or 0
            p = row['present'] or 0
            row['percentage'] = round((p / t * 100), 2) if t > 0 else 0
            
        return render_template('faculty/report.html', report_data=report_data)
    finally:
        cursor.close()
        conn.close()

@attendance_bp.route('/report/student/<student_id>', methods=['GET'])
@faculty_required
def student_report(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            flash('Student not found.', 'danger')
            return redirect(url_for('attendance.report'))
            
        cursor.execute("""
            SELECT attendance_date, status, marked_by
            FROM attendance
            WHERE student_id = %s
            ORDER BY attendance_date DESC
        """, (student_id,))
        history = cursor.fetchall()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(status = 'Present') as present,
                SUM(status = 'Absent') as absent
            FROM attendance
            WHERE student_id = %s
        """, (student_id,))
        stats = cursor.fetchone()
        
        t = stats['total'] or 0
        p = stats['present'] or 0
        a = stats['absent'] or 0
        percentage = round((p / t * 100), 2) if t > 0 else 0
        
        return render_template('faculty/student_report.html', 
                               student=student, 
                               history=history, 
                               total=t, present=p, absent=a, 
                               percentage=percentage)
    finally:
        cursor.close()
        conn.close()

@attendance_bp.route('/daily_report', methods=['GET'])
@faculty_required
def daily_report():
    date_str = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT s.student_id, s.name, a.status 
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
            WHERE a.attendance_date = %s
        """, (date_str,))
        records = cursor.fetchall()
        
        present = sum(1 for r in records if r['status'] == 'Present')
        absent = sum(1 for r in records if r['status'] == 'Absent')
        total = len(records)
        
        return render_template('faculty/daily_report.html', 
                               records=records, 
                               date=date_str,
                               present=present,
                               absent=absent,
                               total=total)
    finally:
        cursor.close()
        conn.close()
