# Project Documentation: Student Attendance Management System

## 1. Project Overview
The **Student Attendance Management System** is a full-stack web application designed to track, manage, and analyze student attendance. It provides two distinct portals: one for **Faculty** to manage students and mark attendance, and one for **Students** to view their academic standing and attendance percentage.

## 2. Technology Stack
* **Backend Framework**: Python 3, Flask
* **Database**: MySQL (relational database management)
* **Database Driver**: `mysql-connector-python`
* **Frontend**: HTML5, CSS3, Bootstrap 5 (CSS Framework)
* **Templating Engine**: Jinja2 (Flask default)
* **Security & Hashing**: Werkzeug Security (`scrypt` algorithm)
* **Environment Management**: `python-dotenv` for securely loading `.env` variables

## 3. System Architecture
The application follows a standard **MVC (Model-View-Controller)** pattern:
* **Model (Database)**: Represented by `sql/schema.sql`. Handles data structuring and relationships.
* **View (Templates)**: Located in the `templates/` folder. Handles what the user sees in the browser.
* **Controller (Routes)**: Located in the `routes/` folder. Acts as the brain, processing form submissions, calculating data, and interacting with the database.

## 4. Database Schema Design

The database consists of three primary tables:

### A. `students` Table
| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `student_id` | VARCHAR(20) | PRIMARY KEY | Unique ID (e.g., MCA2026001) |
| `name` | VARCHAR(100) | NOT NULL | Full name of the student |
| `email` | VARCHAR(150) | UNIQUE, NOT NULL | Student email for contact |
| `password` | VARCHAR(255) | NOT NULL | Hashed password |
| `phone` | VARCHAR(20) | NULL | Contact number |
| `course` | VARCHAR(100) | NULL | Enrolled course (e.g., MCA) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT | Record creation time |

### B. `faculty` Table
| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `faculty_id` | VARCHAR(20) | PRIMARY KEY | Unique Faculty ID (e.g., F101) |
| `name` | VARCHAR(100) | NOT NULL | Full name of the faculty |
| `email` | VARCHAR(150) | UNIQUE, NOT NULL | Faculty email |
| `password` | VARCHAR(255) | NOT NULL | Hashed password |
| `phone` | VARCHAR(20) | NULL | Contact number |

### C. `attendance` Table
| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| `attendance_id` | INT | PRIMARY KEY, A_I | Auto Increment Unique ID |
| `student_id` | VARCHAR(20) | FK, NOT NULL | Links to `students` table |
| `attendance_date` | DATE | NOT NULL | Date of the class |
| `status` | ENUM | NOT NULL | 'Present' or 'Absent' |
| `marked_by` | VARCHAR(20) | FK, NOT NULL | Links to `faculty` table |

**Key Constraints**: 
* `FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE` ensures that if a student is removed from the system, their attendance history is automatically wiped to prevent orphaned data.
* `UNIQUE(student_id, attendance_date)` ensures a student cannot have two attendance records for the same day.

## 5. Security Implementations
* **Password Hashing**: Passwords are mathematically hashed using `generate_password_hash()` before entering the database. Plain-text passwords are never saved.
* **Session Management**: Upon successful login, the server issues an encrypted session cookie containing the user's `role` ('student' or 'faculty'). 
* **Role-Based Access Control (RBAC)**: Custom Python decorators (`@student_required`, `@faculty_required`) check the session cookie on every request. If a student attempts to load a faculty URL, the server instantly terminates the request with a `403 Forbidden` error.
* **SQL Injection Prevention**: All `mysql.connector` queries use parameterized inputs (e.g., `execute("... WHERE id = %s", (id,))`). This completely nullifies SQL injection attacks.
* **Environment Variables**: Sensitive data (DB Password, Flask Secret Key) are hidden inside a `.env` file that is ignored by Git, preventing accidental leaks to public repositories.

## 6. Route & Feature Structure

### Auth Routes (`/`)
* `GET /`: Landing page asking user to select their portal.
* `GET/POST /student/login`: Authenticates students.
* `GET/POST /faculty/login`: Authenticates faculty.
* `GET /logout`: Clears the session and redirects to login.

### Student Routes (`/student`)
* `GET /dashboard`: Main hub showing calculated attendance statistics.
* `GET/POST /profile`: Allows the student to view and update contact information.
* `GET /attendance`: View historical attendance logs sorted by date.
* `GET/POST /change_password`: Allows students to securely update their password.

### Faculty Routes (`/faculty`)
* `GET /dashboard`: Summary statistics of the whole system (total students, daily presence).
* `GET /students`: List all students. Includes a search feature.
* `GET/POST /students/add`: Register a new student into the system.
* `GET/POST /students/edit/<id>`: Update a student's information.
* `POST /students/delete/<id>`: Permanently remove a student.

### Attendance Routes (`/faculty/attendance`)
* `GET/POST /mark`: Form to mark today's or past attendance for all students.
* `POST /update`: Quick-action to fix an incorrectly marked attendance status.
* `GET /report`: Aggregated view showing the attendance percentage of every student.
* `GET /daily_report`: Filter attendance by a specific date.
* `GET /report/student/<id>`: Deep dive into a specific student's full attendance history.

## 7. Future Enhancements (Optional)
If this project were to be expanded, the following features could be added:
* **Email Notifications**: Automatically send an email to a student if their attendance drops below 75%.
* **Export to Excel/PDF**: Allow faculty to download attendance reports.
* **Multi-Course Management**: Add tables for `Courses` and `Subjects` to track attendance per specific class rather than globally.
