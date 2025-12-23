import cv2
from google.protobuf import symbol_database, message_factory

# Patch SymbolDatabase to include GetPrototype
if not hasattr(symbol_database.Default(), "GetPrototype"):
    def get_prototype(self, descriptor):
        return message_factory.MessageFactory().GetPrototype(descriptor)
    symbol_database.Default().GetPrototype = get_prototype

import mediapipe as mp
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ===================== AUDIO SETUP (ONCE) =====================
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)
volume = cast(interface, POINTER(IAudioEndpointVolume))

min_vol, max_vol, _ = volume.GetVolumeRange()

# ===================== MEDIAPIPE SETUP =====================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# ===================== MAIN LOOP =====================
with mp_hands.Hands(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5
) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                # Thumb & index
                thumb = hand_landmarks.landmark[
                    mp_hands.HandLandmark.THUMB_TIP
                ]
                index = hand_landmarks.landmark[
                    mp_hands.HandLandmark.INDEX_FINGER_TIP
                ]

                x1, y1 = int(thumb.x * w), int(thumb.y * h)
                x2, y2 = int(index.x * w), int(index.y * h)

                cv2.circle(frame, (x1, y1), 8, (255, 0, 0), -1)
                cv2.circle(frame, (x2, y2), 8, (255, 0, 0), -1)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                # Distance
                distance = np.hypot(x2 - x1, y2 - y1)
                distance = np.clip(distance, 30, 250)

                # Convert distance → volume
                vol_db = np.interp(distance, [30, 250], [min_vol, max_vol])
                volume.SetMasterVolumeLevel(vol_db, None)

                # UI values
                vol_percent = int(np.interp(distance, [30, 250], [0, 100]))
                vol_bar = np.interp(vol_percent, [0, 100], [400, 150])

                # Volume bar
                cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 2)
                cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (0, 255, 0), -1)

                cv2.putText(
                    frame,
                    f'Volume: {vol_percent}%',
                    (40, 430),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

        cv2.imshow("Gesture Volume Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
