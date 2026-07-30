from datetime import datetime
import cv2
import sqlite3
import os
print("Database Path:", os.path.abspath("database/attendance.db"))

# -----------------------------
# Load Trained Model
# -----------------------------
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/trainer.yml")

# -----------------------------
# Load Haar Cascade
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -----------------------------
# Open Webcam
# -----------------------------
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Error: Cannot open webcam")
    exit()

print("Webcam Started... Press ESC to Exit")

# -----------------------------
# Face Recognition Loop
# -----------------------------
exit_camera = False
while True:

    ret, frame = cam.read()

    if not ret:
        print("Failed to capture frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100, 100)
    )

    for (x, y, w, h) in faces:

        face = gray[y:y+h, x:x+w]

        student_id, confidence = recognizer.predict(face)
        print(f"predicted ID: {student_id}, confidence: {confidence}")

        color = (0, 0, 255)
        text = f"Unknown ({100 - int(confidence)}%)"

        if confidence < 70:

            print("Predicted ID:", student_id)

            conn = sqlite3.connect("database/attendance.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM students WHERE student_id=?",
                (student_id,)
            )

            result = cursor.fetchone()

            print("Student Query Result:", result)

            if result:
                print("Student Found")

                name = result[0]

                color = (0, 255, 0)
                confidence_text = f"{100 - int(confidence)}%"
                text = f"{name} | ID:{student_id} | {confidence_text}"

                today = datetime.now().strftime("%Y-%m-%d")
                current_time = datetime.now().strftime("%H:%M:%S")

                cursor.execute(
                    """
                    SELECT * FROM attendance
                    WHERE student_id=? AND date=?
                    """,
                    (student_id, today)
                )

                already_marked = cursor.fetchone()
                print("Already Marked:", already_marked)

                if already_marked is None:
                    cursor.execute("""
                        INSERT INTO attendance
                        (student_id, name, date, time)
                        VALUES (?, ?, ?, ?)
                    """, (student_id, name, today, current_time))

                    conn.commit()

                    print(f"✅ Attendance Marked: {name}")

                    cv2.putText(
                        frame,
                        "Attendance Marked Successfully",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                    cv2.imshow("AI Face Recognition Attendance", frame)
                    cv2.waitKey(2000)

                    cam.release()
                    cv2.destroyAllWindows()
                    exit_camera = True
                    break
                else:

                    print("⚠ Attendance Already Marked")

                    cv2.putText(
                        frame,
                        "Attendance Already Marked",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )

                    cv2.imshow("AI Face Recognition Attendance", frame)
                    cv2.waitKey(2000)

                    cam.release()
                    cv2.destroyAllWindows()
                    exit_camera = True
                    break


            conn.close()

        # Draw Rectangle
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                color,
                3
            )

        # Display Name
        cv2.putText(
            frame,
            text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )
        current = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        cv2.putText(
            frame,
            current,
            (10, frame.shape[0] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    # Show Webcam
    cv2.imshow("AI Face Recognition Attendance", frame)

    # Press ESC to Exit
    if cv2.waitKey(1) & 0xFF == 27:
        exit_camera = True
        break

# -----------------------------
# Release Resources
# -----------------------------
cam.release()
cv2.destroyAllWindows()

print("Face Recognition Closed")