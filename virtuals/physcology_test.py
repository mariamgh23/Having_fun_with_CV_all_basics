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

# Questions for the psychology game
questions = [
    "1. You often find yourself planning things in detail before taking action.",
    "2. You feel uncomfortable when someone criticizes you in front of others.",
    "3. You enjoy meeting new people, even if it makes you a little anxious.",
    "4. When a friend asks for help, you put their needs above your own.",
    "5. You find it difficult to stick to a routine.",
    "6. You often make decisions based on logic rather than emotions.",
    "7. You feel drained after spending a lot of time in social situations.",
    "8. You tend to forgive people easily, even if they hurt you.",
    "9. You enjoy taking risks, even if there's a chance of failure.",
    "10. You feel anxious when things are unpredictable or chaotic."
]

# Game state variables
current_question_idx = 0
answers = []  # Store True for OK (thumbs up), False for Not OK (thumbs down)
game_state = "question"  # States: "question", "answered", "results"
answered_gesture = None  # Track what gesture was detected

# Next button (top-right corner)
next_button = {"x": 1050, "y": 30, "width": 200, "height": 80, "text": "NEXT"}

# Cooldown for gestures
gesture_cooldown = 0
cooldown_frames = 30

def is_thumb_up(hand_landmarks, handedness):
    """Check if thumb is pointing up"""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    
    thumb_extended = thumb_tip.y < thumb_ip.y < thumb_mcp.y
    
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
    
    thumb_extended = thumb_tip.y > thumb_ip.y > thumb_mcp.y
    
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

def detect_next_button(x, y):
    """Detect if pointing at next button"""
    if (next_button["x"] < x < next_button["x"] + next_button["width"] and 
        next_button["y"] < y < next_button["y"] + next_button["height"]):
        return True
    return False

def draw_next_button(frame, hover=False):
    """Draw the NEXT button with transparency"""
    overlay = frame.copy()
    
    if game_state == "answered":
        color = (255, 200, 100) if hover else (200, 150, 0)
        alpha = 0.7 if hover else 0.5
    else:
        color = (100, 100, 100)
        alpha = 0.3
    
    cv2.rectangle(overlay, (next_button["x"], next_button["y"]), 
                 (next_button["x"] + next_button["width"], next_button["y"] + next_button["height"]), 
                 color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.rectangle(frame, (next_button["x"], next_button["y"]), 
                 (next_button["x"] + next_button["width"], next_button["y"] + next_button["height"]), 
                 (255, 255, 255), 3)
    cv2.putText(frame, next_button["text"], (next_button["x"] + 35, next_button["y"] + 55), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

def analyze_personality(answers):
    """Analyze personality based on answers"""
    adventurous_questions = [0, 2, 5, 8]
    empathetic_questions = [1, 3, 6, 7, 9]
    
    adventurous_score = sum(1 for i in adventurous_questions if i < len(answers) and answers[i])
    empathetic_score = sum(1 for i in empathetic_questions if i < len(answers) and answers[i])
    
    result = ""
    
    if adventurous_score >= 3:
        result += "EXTROVERTED & ADVENTUROUS\n"
        result += "You enjoy challenges and are a practical thinker.\n"
        result += "You thrive on new experiences and taking action.\n"
    elif empathetic_score >= 4:
        result += "EMPATHETIC & CAUTIOUS\n"
        result += "You value relationships and are sensitive to your surroundings.\n"
        result += "You care deeply about others and prefer stability.\n"
    else:
        result += "BALANCED PERSONALITY\n"
        result += "You can adapt between social/explorative and\n"
        result += "introspective/caring modes depending on the situation.\n"
        result += "You have a flexible approach to life.\n"
    
    return result

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if gesture_cooldown > 0:
            gesture_cooldown -= 1

        # Draw UI
        if game_state == "results":
            overlay = frame.copy()
            cv2.rectangle(overlay, (50, 50), (1230, 670), (50, 50, 50), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            cv2.rectangle(frame, (50, 50), (1230, 670), (255, 255, 255), 3)
            
            cv2.putText(frame, "PERSONALITY ASSESSMENT RESULTS", (150, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            
            result_text = analyze_personality(answers)
            lines = result_text.split('\n')
            y_pos = 220
            for i, line in enumerate(lines):
                if i == 0:
                    cv2.putText(frame, line, (150, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 0), 3)
                else:
                    cv2.putText(frame, line, (150, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                y_pos += 70
            
            cv2.putText(frame, "Press 'R' to restart or 'Q' to quit", (300, 630), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
        else:
            overlay = frame.copy()
            cv2.rectangle(overlay, (30, 30), (1250, 250), (50, 50, 50), -1)
            cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
            cv2.rectangle(frame, (30, 30), (1250, 250), (255, 255, 255), 3)
            
            cv2.putText(frame, f"Question {current_question_idx + 1}/10", (50, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            question_text = questions[current_question_idx]
            words = question_text.split()
            line1 = ""
            line2 = ""
            for word in words:
                if len(line1) < 60:
                    line1 += word + " "
                else:
                    line2 += word + " "
            
            cv2.putText(frame, line1, (50, 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            if line2:
                cv2.putText(frame, line2, (50, 190), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            
            cv2.putText(frame, "Thumbs UP = OK  |  Thumbs DOWN = Not OK", (350, 300), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
            
            if game_state == "answered":
                if answered_gesture == "OK":
                    cv2.putText(frame, "Your Answer: OK", (500, 400), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
                else:
                    cv2.putText(frame, "Your Answer: NOT OK", (450, 400), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
                cv2.putText(frame, "Click NEXT to continue", (470, 550), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)

        hover_next = False
        thumbs_up_detected = False
        thumbs_down_detected = False
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, _ = frame.shape
                index_x = int(index_finger_tip.x * w)
                index_y = int(index_finger_tip.y * h)
                
                cv2.circle(frame, (index_x, index_y), 15, (255, 0, 255), -1)
                
                if detect_next_button(index_x, index_y):
                    hover_next = True
                    if game_state == "answered" and gesture_cooldown == 0:
                        current_question_idx += 1
                        if current_question_idx >= len(questions):
                            game_state = "results"
                        else:
                            game_state = "question"
                            answered_gesture = None
                        gesture_cooldown = cooldown_frames
                
                if game_state == "question" and gesture_cooldown == 0:
                    if is_thumb_up(hand_landmarks, handedness):
                        thumbs_up_detected = True
                    elif is_thumb_down(hand_landmarks, handedness):
                        thumbs_down_detected = True
        
        if game_state == "question":
            if thumbs_up_detected and gesture_cooldown == 0:
                answers.append(True)
                answered_gesture = "OK"
                game_state = "answered"
                gesture_cooldown = cooldown_frames
            elif thumbs_down_detected and gesture_cooldown == 0:
                answers.append(False)
                answered_gesture = "NOT OK"
                game_state = "answered"
                gesture_cooldown = cooldown_frames
        
        if game_state != "results":
            draw_next_button(frame, hover_next)

        cv2.imshow("Psychology Assessment Game", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r') and game_state == "results":
            current_question_idx = 0
            answers = []
            game_state = "question"
            answered_gesture = None
            gesture_cooldown = 0

cap.release()
cv2.destroyAllWindows()
