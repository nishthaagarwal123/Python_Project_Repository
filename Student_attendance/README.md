# Student Attendance Management System

A complete web-based Student Attendance Management System built with Python, Flask, and MySQL. It features two user roles: Student and Faculty, each with specific permissions and dashboards.

## Features

* **Student Login & Faculty Login**: Separate authentication workflows.
* **Student Dashboard**: View personal profile, attendance history, and attendance percentage.
* **Faculty Dashboard**: Manage students (CRUD) and attendance.
* **Attendance Management**: Mark attendance, update existing records, and generate reports.
* **Attendance Reports**: Individual student reports, daily attendance, and overall statistics.
* **MySQL Database**: Stores users and attendance data securely.
* **Password Hashing**: Uses Werkzeug's `scrypt` hashing for secure password storage.
* **Role-Based Authorization**: Protected routes to prevent unauthorized access.

## Requirements

* Python 3
* MySQL Server
* MySQL Workbench (optional, for running SQL scripts visually)

## Installation

1. **Clone or Download the Project**.
2. **Create a Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   ```
3. **Activate the Virtual Environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. Open **MySQL Workbench**.
2. Connect to your local MySQL Server (`localhost:3306`).
3. Open the `sql/schema.sql` script and execute it. This will create the `student_attendance` database and tables.
4. Open the `sql/seed.sql` script and execute it. This will insert sample data.

### Sample Login Credentials (from seed.sql):
* **Student**: ID `101`, Password `password123`
* **Student**: ID `102`, Password `password123`
* **Student**: ID `103`, Password `password123`
* **Faculty**: ID `F101`, Password `faculty123`

## Environment Setup

Create a `.env` file in the root directory (copy from `.env.example`).
Update the credentials if necessary to match your MySQL database settings.

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=student_attendance
SECRET_KEY=change-this-secret-key
```
*(Note: Never commit your `.env` file to version control. The `.gitignore` is already configured for this.)*

## Run Application

1. Make sure your virtual environment is activated and `.env` is properly configured.
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000/
   ```

## Technical Explanations

### 1. Database Relationships
* `students` table: Stores student profiles and hashed passwords.
* `faculty` table: Stores faculty profiles and hashed passwords.
* `attendance` table: Links to `students` and `faculty` via foreign keys. Uses `UNIQUE(student_id, attendance_date)` to prevent duplicate marking on the same day. `ON DELETE CASCADE` ensures student deletion also removes their attendance.

### 2. Authentication & Student/Faculty Login
When a user logs in, the `app` queries the database by their ID. It verifies the password using `check_password_hash`. If successful, the `app` sets the `session['role']` to either `'student'` or `'faculty'` along with their ID. 
The system uses custom decorators (`@student_required`, `@faculty_required`) inside `utils.py` to protect specific routes based on the current session role.

### 3. Security
* Passwords are never stored as plain text. Werkzeug generates a secure hash.
* `mysql.connector` parameterized queries (`%s`) are used in all database interactions to prevent SQL injection.
* Database credentials are kept out of the source code via the `.env` file.
* Role-based checks prevent students from accessing faculty pages (e.g., manually typing `/faculty/dashboard` will result in a `403 Forbidden` error).

## Testing Scenarios
- **Student Flow**: Login with `101` / `password123` -> Check Profile -> Check Attendance -> Change Password -> Logout.
- **Faculty Flow**: Login with `F101` / `faculty123` -> Add a new student -> Go to Mark Attendance -> Select today's date -> Submit -> Update attendance -> View Reports.
- **Security**: Attempt to access `http://127.0.0.1:5000/faculty/dashboard` while logged in as a student (will deny access).
