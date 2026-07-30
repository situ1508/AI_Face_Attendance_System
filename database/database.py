import sqlite3

conn = sqlite3.connect("database/attendance.db")
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    student_id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    semester TEXT,
    section TEXT,
    email TEXT,
    phone TEXT
)
""")

# Attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    name TEXT,
    date TEXT,
    time TEXT,
    status TEXT
)
""")

# Departments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT
)
""")

# Subjects table
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT,
    department TEXT
)
""")

# Default admin
cursor.execute("""
INSERT OR IGNORE INTO users(username, password)
VALUES ('admin', 'admin123')
""")


conn.commit()
conn.close()

print("Database created successfully!")
