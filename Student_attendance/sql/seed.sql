USE student_attendance;

-- Insert students with hashed password 'password123'
INSERT INTO students (student_id, name, email, password, phone, course) VALUES 
('MCA2026001', 'Nitin', 'nitin@example.com', 'scrypt:32768:8:1$lo7lScODgzTOUaqb$8bbcf62e4e6663b1b6fb7db1b15b5b3e732a30b29a14a516d2671a4f5aa152f08db90bd5c6299e9214c78c7c8f3c4385e65422cdec94502c61c8ee0a9139524d', '1234567890', 'MCA'),
('MCA2026002', 'Rahul', 'rahul@example.com', 'scrypt:32768:8:1$lo7lScODgzTOUaqb$8bbcf62e4e6663b1b6fb7db1b15b5b3e732a30b29a14a516d2671a4f5aa152f08db90bd5c6299e9214c78c7c8f3c4385e65422cdec94502c61c8ee0a9139524d', '0987654321', 'MCA'),
('MCA2026003', 'Aman', 'aman@example.com', 'scrypt:32768:8:1$lo7lScODgzTOUaqb$8bbcf62e4e6663b1b6fb7db1b15b5b3e732a30b29a14a516d2671a4f5aa152f08db90bd5c6299e9214c78c7c8f3c4385e65422cdec94502c61c8ee0a9139524d', '1112223333', 'MCA');

-- Insert faculty with hashed password 'faculty123'
INSERT INTO faculty (faculty_id, name, email, password, phone) VALUES 
('F101', 'Amit Sharma', 'amit@example.com', 'scrypt:32768:8:1$4eg7rBNPGsEjBHi1$7804e89ba0dea2aaa78fa08fcc0197d257758f7f980b102956c509b3cecdd4f738f91404717a772ceb15293624d2f3b2aa441514f8db24e63da8269fde6cd492', '5556667777');

-- Insert some attendance records
INSERT INTO attendance (student_id, attendance_date, status, marked_by) VALUES
('MCA2026001', '2026-10-01', 'Present', 'F101'),
('MCA2026002', '2026-10-01', 'Absent', 'F101'),
('MCA2026003', '2026-10-01', 'Present', 'F101'),
('MCA2026001', '2026-09-30', 'Present', 'F101'),
('MCA2026002', '2026-09-30', 'Present', 'F101'),
('MCA2026003', '2026-09-30', 'Absent', 'F101');
