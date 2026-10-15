from werkzeug.security import generate_password_hash
print("student_hash:", generate_password_hash("password123"))
print("faculty_hash:", generate_password_hash("faculty123"))
