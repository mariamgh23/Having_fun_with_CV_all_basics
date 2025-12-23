import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import warnings
import os
warnings.filterwarnings("ignore")

# Print current directory to debug
print("Current directory:", os.getcwd())

# Use full path to your model
model = load_model(r"C:\Users\maria\OneDrive\Desktop\CV project\Emotion_detection\best_model.h5")

# Rest of your code...
emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

face_haar_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("Press 'q' to quit")

def predict_emotion(face):
    """Preprocess face and predict emotion"""
    roi_rgb = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
    roi_rgb = cv2.resize(roi_rgb, (224, 224))
    img_pixels = img_to_array(roi_rgb)
    img_pixels = np.expand_dims(img_pixels, axis=0) / 255.0
    preds = model.predict(img_pixels, verbose=0)
    emotion = emotions[np.argmax(preds)]
    return emotion

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_haar_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            emotion = predict_emotion(roi_gray)
            cv2.putText(frame, emotion, (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Facial Emotion Analysis", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    cap.release()
    cv2.destroyAllWindows()