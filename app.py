from openpyxl import Workbook
import sys
import sqlite3
from flask import Flask, render_template, request, redirect, send_file
import subprocess
import os
import cv2
import os
print("Database Path:", os.path.abspath("database/attendance.db"))

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    print("Username entered =", repr(username))
    print("Password entered =", repr(password))

    if username == "admin" and password == "admin123":
        print("Login Successful")
        return redirect("/dashboard")

    print("Login Failed")
    return "Invalid Username or Password"

from datetime import datetime

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    # Statistics
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today,))
    present_today = cursor.fetchone()[0]

    absent = total_students - present_today

    cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
    total_departments = cursor.fetchone()[0]

    # Today's attendance (latest 5)
    cursor.execute("""
        SELECT name,time
        FROM attendance
        WHERE date=?
        ORDER BY time DESC
        LIMIT 5
    """, (today,))
    today_records = cursor.fetchall()

    # Recent attendance (latest 10)
    cursor.execute("""
        SELECT student_id,name,date,time
        FROM attendance
        ORDER BY id DESC
        LIMIT 10
    """)
    recent_records = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        present_today=present_today,
        absent=absent,
        total_departments=total_departments,
        today_records=today_records,
        recent_records=recent_records
    )
@app.route("/students")
def students():

    search = request.args.get("search", "")

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM students
            WHERE student_id LIKE ?
               OR name LIKE ?
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    return render_template("student_menu.html")

@app.route("/new_student")
def new_student():
    return render_template("new_student.html")

@app.route("/registered_students")
def registered_students():

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    # Students List
    cursor.execute("""
        SELECT student_id, name, department, semester
        FROM students
        ORDER BY student_id
    """)
    students = cursor.fetchall()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Departments
    cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
    total_departments = cursor.fetchone()[0]

    # Face Dataset Count
    cursor.execute("SELECT COUNT(*) FROM students")
    face_registered = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "registered_students.html",
        students=students,
        total_students=total_students,
        total_departments=total_departments,
        face_registered=face_registered
    )
@app.route("/view_students")
def view_students():

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("view_students.html", students=students)
@app.route("/add_student", methods=["POST"])
def add_student():

    student_id = request.form["student_id"]
    name = request.form["name"]
    department = request.form["department"]
    semester = request.form["semester"]
    section = request.form["section"]
    email = request.form["email"]
    phone = request.form["phone"]

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO students
        (student_id, name, department, semester, section, email, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_id, name, department, semester, section, email, phone))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return "❌ Student ID already exists. Please use another Student ID."

    conn.close()

    return redirect("/students")
@app.route("/update_student", methods=["POST"])
def update_student():

    student_id = request.form["student_id"]
    name = request.form["name"]
    department = request.form["department"]
    semester = request.form["semester"]
    section = request.form["section"]
    email = request.form["email"]
    phone = request.form["phone"]

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET
            name = ?,
            department = ?,
            semester = ?,
            section = ?,
            email = ?,
            phone = ?
        WHERE student_id = ?
    """, (name, department, semester, section, email, phone, student_id))

    conn.commit()
    conn.close()

    return redirect("/students")
@app.route("/capture_face/<int:student_id>")
def capture_face(student_id):

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, name, department
        FROM students
        WHERE student_id=?
    """, (student_id,))

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "capture_face.html",
        student=student
    )
@app.route("/start_capture/<int:student_id>")
def start_capture(student_id):

    print("Starting capture for:", student_id)

    result = subprocess.run(
        [
            sys.executable,
            "capture/capture_faces.py",
            str(student_id)
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    return redirect("/registered_students")
@app.route("/edit_student/<int:student_id>")
def edit_student(student_id):

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE student_id=?",
        (student_id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template("edit_student.html", student=student)

@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):

    print("Deleting Student ID:", student_id)

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE student_id=?",
        (student_id,)
    )

    print("Rows Deleted:", cursor.rowcount)

    conn.commit()
    conn.close()

    return redirect("/students")

@app.route("/start_attendance")
def start_attendance():

    subprocess.run([
        sys.executable,
        "recognizer/recognizer.py"
    ])

    return redirect("/attendance")
from datetime import datetime

@app.route("/attendance")
def attendance():

    selected_date = request.args.get(
        "date",
        datetime.now().strftime("%Y-%m-%d")
    )

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, name, date, time
        FROM attendance
        WHERE date=?
        ORDER BY time DESC
    """, (selected_date,))
    records = cursor.fetchall()
    print("Attendance Records:", records)

    # Dashboard statistics
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    present_today = len(records)
    absent_today = total_students - present_today

    attendance_percentage = 0
    if total_students > 0:
        attendance_percentage = round((present_today / total_students) * 100)

    conn.close()

    return render_template(
        "attendance.html",
        records=records,
        selected_date=selected_date,
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        attendance_percentage=attendance_percentage
    )
@app.route("/reports")
def reports():

    selected_date = request.args.get(
        "date",
        datetime.now().strftime("%Y-%m-%d")
    )

    search = request.args.get("search", "")

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Attendance Records
    if search:

        cursor.execute("""
            SELECT student_id,name,date,time
            FROM attendance
            WHERE date=?
            AND (
                student_id LIKE ?
                OR name LIKE ?
            )
            ORDER BY time DESC
        """, (
            selected_date,
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT student_id,name,date,time
            FROM attendance
            WHERE date=?
            ORDER BY time DESC
        """, (selected_date,))

    records = cursor.fetchall()

    present = len(records)
    absent = total_students - present

    attendance_percentage = 0

    if total_students > 0:
        attendance_percentage = round(
            (present / total_students) * 100
        )

    conn.close()

    return render_template(
        "reports.html",
        records=records,
        selected_date=selected_date,
        search=search,
        total_students=total_students,
        present=present,
        absent=absent,
        attendance_percentage=attendance_percentage
    )
@app.route("/train_model")
def train_model():

    return render_template("train_model.html")
@app.route("/start_training")
def start_training():

    subprocess.run([
        sys.executable,
        "trainer/train.py"
    ])

    return render_template("training_success.html")

@app.route("/export_excel")
def export_excel():

    conn = sqlite3.connect("database/attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, name, date, time
        FROM attendance
        ORDER BY date DESC, time DESC
    """)

    records = cursor.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Report"

    ws.append([
        "Student ID",
        "Name",
        "Date",
        "Time"
    ])

    for row in records:
        ws.append(row)

    filename = "attendance_report.xlsx"
    wb.save(filename)

    return send_file(
        filename,
        as_attachment=True
    )
if __name__ == "__main__":
    app.run(debug=True)