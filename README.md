![Python](https://img.shields.io/badge/Python-3.9+-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Deep%20Learning-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Object%20Detection-purple)

# 🎯 Resume Section: Projects

**Having Fun with Computer Vision**
**Python, TensorFlow, OpenCV, Streamlit, YOLOv8, MediaPipe**

* Built a multi-feature computer vision system integrating emotion recognition, hand tracking, gesture-based controls, and real-time object detection.

* Designed and trained a MobileNet-based CNN achieving accurate 7-class facial emotion classification.

* Developed a centralized Streamlit dashboard to launch multiple real-time vision modules.

* Implemented gesture-based volume control using MediaPipe Hands and system-level audio APIs.

* Integrated YOLOv8 for real-time object detection with webcam inference.

* Engineered modular, portable codebase suitable for cross-platform deployment.



# 🌟 Features
## 😊 Emotion Detection

**Real-time facial emotion recognition using a MobileNet-based CNN**

**Trained on a Kaggle facial emotion dataset** (https://www.kaggle.com/datasets/ananthu017/emotion-detection-fer)

Detects 7 emotions:

* Angry

* Disgust

* Fear

* Happy

* Neutral

* Sad

* Surprise

## ✋ Hand Tracking

**Real-time hand landmark detection using MediaPipe Hands**

* Finger counting and thumb direction detection

* Smooth and stable tracking

## 🔊 Volume Gesture Control

**Control system volume using thumb–index finger distance**

**Built with MediaPipe + Pycaw (Windows)**

**Visual feedback with dynamic volume bar**

## 🎮 Virtual Games (Gesture-Controlled)

**Interactive games controlled entirely using hand gestures:**

### Guessing Game – virtual keyboard interaction

### Psychology Test – gesture-based personality test

### Tic-Tac-Toe – play against the computer using hand movements

## 🔍 YOLOv8 Object Detection & Tracking

**Real-time object detection using YOLOv8 (Ultralytics)**

* Webcam-based inference

* Automatic model download and recovery

* Bounding boxes with class labels

## 🧠 Emotion Detection Model Details

**Backbone: MobileNet (pretrained on ImageNet)**

### Custom Head:

* Global Average Pooling

* Dense (512, ReLU)

* Dropout (0.5)

* Softmax (7 classes)

* Optimizer: Adam (learning rate = 1e-4)

* Loss Function: Categorical Crossentropy

# 📁 Project Structure

```
Having-Fun-with-Computer-Vision/
├── Emotion_detection/
│   ├── em_de.ipynb
│   ├── emotion_webcam.py
│   └── best_model.h5
│
├── pose_detection/
│   └── hand_tracking.py
│
├── virtuals/
│   ├── guessing_game.py
│   ├── psychology_test.py
│   ├── tic_tac_toe.py
│   └── volume_gesture_control.py
│
├── yolo_webcam_detection/
│   └── Tracking.py
│
├── cv_project_ui.py
├── requirements.txt
└── README.md
```
# 📊 Dataset

**Source: Kaggle Facial Emotion Dataset(https://www.kaggle.com/datasets/ananthu017/emotion-detection-fer)**

Images resized to **224 × 224**

Organized into
train/ and test/ folders

**⚠️ The dataset is not included in this repository.**

Expected structure:
```
Emotion_detection/
├── train/
└── test/
```
# ⚙️ Installation
```
git clone https://github.com/your-username/Having-Fun-with-Computer-Vision.git
cd Having-Fun-with-Computer-Vision
pip install -r requirements.txt
```
> ⚠️ Python 3.9+ is recommended.

# ▶️ Run the Main Application (Recommended)
```
streamlit run cv_project_ui.py
```
This launches a central dashboard from which all features can be started.
# ▶️ Run Individual Modules (Optional)
```
python Emotion_detection/emotion_webcam.py
python pose_detection/hand_tracking.py
python virtuals/volume_gesture_control.py
python yolo_webcam_detection/Tracking.py
```
# 🧪 Technologies Used

* Python

* TensorFlow / Keras

* OpenCV

* MediaPipe

* Streamlit

* YOLOv8 (Ultralytics)

* NumPy, Pandas, Matplotlib

# 🚀 Future Enhancements

* Cross-platform volume gesture support

* Face alignment for improved emotion recognition

* Dockerized deployment

* Web and mobile deployment

* Performance optimization for low-end devices

# 👩‍💻 Author

**Mariam Ghareeb**
**Computer Vision & Deep Learning Enthusiast**

#  License

**This project is licensed under the MIT License.**

# ⭐ If you find this project useful

**Please consider starring ⭐ the repository — it helps others discover the project!**
