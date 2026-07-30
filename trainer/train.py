import cv2
import numpy as np
from PIL import Image
import os

# Create LBPH Face Recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

dataset_path = "dataset"

faces = []
ids = []

# Read all student folders
for student_id in os.listdir(dataset_path):

    student_folder = os.path.join(dataset_path, student_id)

    if not os.path.isdir(student_folder):
        continue

    for image_name in os.listdir(student_folder):

        image_path = os.path.join(student_folder, image_name)

        img = Image.open(image_path).convert("L")
        image_np = np.array(img, "uint8")

        faces.append(image_np)
        ids.append(int(student_id))

print(f"Total Images : {len(faces)}")
print(f"Total Students : {len(set(ids))}")

recognizer.train(faces, np.array(ids))

os.makedirs("trainer", exist_ok=True)

recognizer.write("trainer/trainer.yml")

print("✅ Model Trained Successfully!")