import cv2
import os
import sys

print("OpenCV Version:", cv2.__version__)

student_id = sys.argv[1]

dataset_path = os.path.join("dataset", str(student_id))
os.makedirs(dataset_path, exist_ok=True)

cascade_path = "capture/haarcascade_frontalface_default.xml"

print("Cascade Path:", os.path.abspath(cascade_path))

face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    print("Haar Cascade could not be loaded")
    exit()

print("Haar Cascade loaded successfully")

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Webcam could not be opened")
    exit()

print(" Webcam opened")

# Open Webcam
cam = cv2.VideoCapture(0)

count = 0

while True:

    ret, frame = cam.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(80, 80)
    )

    print("Faces detected:", len(faces))

    for (x, y, w, h) in faces:

        count += 1

        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (200, 200))

        filename = os.path.join(dataset_path, f"{count}.jpg")
        cv2.imwrite(filename, face)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

        cv2.putText(
            frame,
            f"Capturing: {count}/100",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    cv2.imshow("Face Capture", frame)

    # Stop after 100 images
    if count >= 100:
        break

    # Press Q to quit early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

print("Face Capture Completed Successfully!")