import cv2
from google.protobuf import symbol_database, message_factory

# Patch SymbolDatabase to include GetPrototype
if not hasattr(symbol_database.Default(), "GetPrototype"):
    def get_prototype(self, descriptor):
        return message_factory.MessageFactory().GetPrototype(descriptor)
    symbol_database.Default().GetPrototype = get_prototype

import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def count_fingers(hand_landmarks, handedness):
    """Count how many fingers are extended"""
    fingers_up = 0
    
    # Get hand label (Left or Right)
    hand_label = handedness.classification[0].label
    
    # Thumb - special case (check x-coordinate instead of y)
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    
    if hand_label == "Right":
        # For right hand, thumb is up if tip is to the right of IP
        if thumb_tip.x < thumb_ip.x:
            fingers_up += 1
    else:
        # For left hand, thumb is up if tip is to the left of IP
        if thumb_tip.x > thumb_ip.x:
            fingers_up += 1
    
    # Other four fingers - check if tip is above PIP joint
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    finger_pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP
    ]
    
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers_up += 1
    
    return fingers_up

def is_thumb_up(hand_landmarks, handedness):
    """Check if thumb is pointing up"""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    
    # Check if thumb is extended upward
    thumb_extended = thumb_tip.y < thumb_ip.y < thumb_mcp.y
    
    # Check if other fingers are folded
    fingers_folded = True
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    finger_pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP
    ]
    
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers_folded = False
            break
    
    return thumb_extended and fingers_folded

def is_thumb_down(hand_landmarks, handedness):
    """Check if thumb is pointing down"""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    
    # Check if thumb is extended downward
    thumb_extended = thumb_tip.y > thumb_ip.y > thumb_mcp.y
    
    # Check if other fingers are folded
    fingers_folded = True
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    finger_pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP
    ]
    
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers_folded = False
            break
    
    return thumb_extended and fingers_folded

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        thumbs_up_count = 0
        thumbs_down_count = 0
        total_fingers = 0
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Draw hand landmarks
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Count fingers
                fingers = count_fingers(hand_landmarks, handedness)
                total_fingers += fingers
                
                # Check for thumbs up or down
                if is_thumb_up(hand_landmarks, handedness):
                    thumbs_up_count += 1
                elif is_thumb_down(hand_landmarks, handedness):
                    thumbs_down_count += 1
        
        # Display information on screen
        cv2.putText(frame, f"Fingers Up: {total_fingers}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"Thumbs Up: {thumbs_up_count}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Thumbs Down: {thumbs_down_count}", (10, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Display gesture status
        if thumbs_up_count > 0:
            cv2.putText(frame, "OK", (frame.shape[1]//2 - 50, frame.shape[0]//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
        elif thumbs_down_count > 0:
            cv2.putText(frame, "NOT OKAY", (frame.shape[1]//2 - 200, frame.shape[0]//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)

        cv2.imshow("Hand Tracking - Finger Counter", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()