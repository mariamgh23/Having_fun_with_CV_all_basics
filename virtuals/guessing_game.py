import cv2
from google.protobuf import symbol_database, message_factory

# Patch SymbolDatabase to include GetPrototype
if not hasattr(symbol_database.Default(), "GetPrototype"):
    def get_prototype(self, descriptor):    
        return message_factory.MessageFactory().GetPrototype(descriptor)
    symbol_database.Default().GetPrototype = get_prototype

import mediapipe as mp
import numpy as np
import random
import json

# Initialize Mediapipe Hand and Drawing Utils
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Desired display size
display_width = 1280
display_height = 720

# Load riddles
riddles = [
    {"sentence": "Something white we drink and have with coffee.", "answer": "MILK"},
    {"sentence": "A yellow fruit that monkeys love.", "answer": "BANANA"},
    {"sentence": "You wear this on your head to keep warm in winter.", "answer": "HAT"},
    {"sentence": "A hot drink people often have in the morning.", "answer": "TEA"},
    {"sentence": "You read this to learn or for fun.", "answer": "BOOK"},
    {"sentence": "A red fruit that grows on trees and is sweet.", "answer": "APPLE"},
    {"sentence": "Something we use to write on paper.", "answer": "PEN"},
    {"sentence": "You wear these on your feet before shoes.", "answer": "SOCKS"},
    {"sentence": "A round object you kick in games.", "answer": "BALL"},
    {"sentence": "Something white that falls from the sky in winter.", "answer": "SNOW"},
    {"sentence": "You sleep on this at night.", "answer": "BED"},
    {"sentence": "You use this to brush your teeth.", "answer": "TOOTHBRUSH"},
    {"sentence": "A big animal with a trunk.", "answer": "ELEPHANT"},
    {"sentence": "You eat this with soup, usually baked.", "answer": "BREAD"},
    {"sentence": "A fruit that is orange and full of juice.", "answer": "ORANGE"},
    {"sentence": "You wear these on your hands in winter.", "answer": "GLOVES"},
    {"sentence": "You use this to call someone.", "answer": "PHONE"},
    {"sentence": "You ride this to go fast on the road.", "answer": "BICYCLE"},
    {"sentence": "A farm animal that gives us eggs.", "answer": "CHICKEN"},
    {"sentence": "Something you wear to see better.", "answer": "GLASSES"},
    {"sentence": "Something that keeps you dry in the rain.", "answer": "UMBRELLA"},
    {"sentence": "A sweet treat made from cocoa.", "answer": "CHOCOLATE"},
    {"sentence": "You cut paper with this.", "answer": "SCISSORS"},
    {"sentence": "A big yellow star in the sky.", "answer": "SUN"},
    {"sentence": "A flying insect that makes honey.", "answer": "BEE"},
    {"sentence": "You wear this on your feet to go outside.", "answer": "SHOES"},
    {"sentence": "A cold dessert that melts in the sun.", "answer": "ICECREAM"},
    {"sentence": "Something we drink when we are thirsty.", "answer": "WATER"},
    {"sentence": "A vehicle with wings that flies.", "answer": "AIRPLANE"},
    {"sentence": "Something you use to take pictures.", "answer": "CAMERA"},
]

# Game variables
current_riddle = None
current_answer = ""
score = 0
total_questions = 0
word = ""
game_state = "playing"  # playing, correct, wrong
message = ""
message_timer = 0

# Define the keyboard layout with better spacing
keyboard_keys = [
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM"
]
key_size = 70
key_padding = 25  # Increased spacing between keys

# Calculate keyboard starting points (at the bottom)
keyboard_start_x = (display_width - (key_size * len(keyboard_keys[0]) + key_padding * (len(keyboard_keys[0]) - 1))) // 2
keyboard_start_y = display_height - 340

# Special buttons - repositioned with more spacing
clear_button = {"x": 80, "y": display_height - 120, "width": 150, "height": 60, "text": "CLEAR"}
submit_button = {"x": 280, "y": display_height - 120, "width": 150, "height": 60, "text": "SUBMIT"}
next_button = {"x": display_width - 200, "y": 30, "width": 150, "height": 60, "text": "NEXT"}  # Moved to top right

# Debounce variables
last_key_pressed = None
key_press_cooldown = 0
cooldown_frames = 15

def get_new_riddle():
    """Get a random riddle"""
    return random.choice(riddles)

def draw_keyboard(frame):
    """Draw the virtual keyboard with better spacing"""
    for i, row in enumerate(keyboard_keys):
        for j, key in enumerate(row):
            x = keyboard_start_x + j * (key_size + key_padding)
            y = keyboard_start_y + i * (key_size + key_padding)
            
            # Draw key background
            cv2.rectangle(frame, (x, y), (x + key_size, y + key_size), (100, 100, 100), -1)
            cv2.rectangle(frame, (x, y), (x + key_size, y + key_size), (255, 255, 255), 3)
            
            # Draw key letter
            text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 1.3, 3)[0]
            text_x = x + (key_size - text_size[0]) // 2
            text_y = y + (key_size + text_size[1]) // 2
            cv2.putText(frame, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3)

def draw_special_buttons(frame):
    """Draw CLEAR, SUBMIT, and NEXT buttons with better spacing"""
    # Clear button
    cv2.rectangle(frame, (clear_button["x"], clear_button["y"]), 
                 (clear_button["x"] + clear_button["width"], clear_button["y"] + clear_button["height"]), 
                 (0, 100, 200), -1)
    cv2.rectangle(frame, (clear_button["x"], clear_button["y"]), 
                 (clear_button["x"] + clear_button["width"], clear_button["y"] + clear_button["height"]), 
                 (255, 255, 255), 3)
    cv2.putText(frame, clear_button["text"], (clear_button["x"] + 15, clear_button["y"] + 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Submit button
    cv2.rectangle(frame, (submit_button["x"], submit_button["y"]), 
                 (submit_button["x"] + submit_button["width"], submit_button["y"] + submit_button["height"]), 
                 (0, 200, 0), -1)
    cv2.rectangle(frame, (submit_button["x"], submit_button["y"]), 
                 (submit_button["x"] + submit_button["width"], submit_button["y"] + submit_button["height"]), 
                 (255, 255, 255), 3)
    cv2.putText(frame, submit_button["text"], (submit_button["x"] + 10, submit_button["y"] + 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Next button (top right - always visible after answering)
    if game_state in ["correct", "wrong"]:
        cv2.rectangle(frame, (next_button["x"], next_button["y"]), 
                     (next_button["x"] + next_button["width"], next_button["y"] + next_button["height"]), 
                     (200, 150, 0), -1)
        cv2.rectangle(frame, (next_button["x"], next_button["y"]), 
                     (next_button["x"] + next_button["width"], next_button["y"] + next_button["height"]), 
                     (255, 255, 255), 3)
        cv2.putText(frame, next_button["text"], (next_button["x"] + 35, next_button["y"] + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)

def detect_key(x, y):
    """Detect which key is being pointed at"""
    for i, row in enumerate(keyboard_keys):
        for j, key in enumerate(row):
            key_x = keyboard_start_x + j * (key_size + key_padding)
            key_y = keyboard_start_y + i * (key_size + key_padding)
            if key_x < x < key_x + key_size and key_y < y < key_y + key_size:
                return key
    return None

def detect_special_button(x, y):
    """Detect if pointing at special buttons"""
    # Check clear button
    if (clear_button["x"] < x < clear_button["x"] + clear_button["width"] and 
        clear_button["y"] < y < clear_button["y"] + clear_button["height"]):
        return "CLEAR"
    
    # Check submit button
    if (submit_button["x"] < x < submit_button["x"] + submit_button["width"] and 
        submit_button["y"] < y < submit_button["y"] + submit_button["height"]):
        return "SUBMIT"
    
    # Check next button (now in top right)
    if (game_state in ["correct", "wrong"] and 
        next_button["x"] < x < next_button["x"] + next_button["width"] and 
        next_button["y"] < y < next_button["y"] + next_button["height"]):
        return "NEXT"
    
    return None

def check_answer(user_answer, correct_answer):
    """Check if the answer is correct"""
    return user_answer.upper().strip() == correct_answer.upper().strip()

# Initialize video capture
video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, display_width)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, display_height)

# Get first riddle
current_riddle = get_new_riddle()
current_answer = current_riddle["answer"]

# Initialize the Hand Tracker
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        # Flip the frame horizontally for a mirror view
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB before processing
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # Decrease cooldown
        if key_press_cooldown > 0:
            key_press_cooldown -= 1

        # Draw background for riddle area
        cv2.rectangle(image_bgr, (20, 20), (display_width - 20, 180), (50, 50, 50), -1)
        cv2.rectangle(image_bgr, (20, 20), (display_width - 20, 180), (255, 255, 255), 2)

        # Display riddle
        riddle_text = current_riddle["sentence"]
        # Split text if too long
        words = riddle_text.split()
        line1 = ""
        line2 = ""
        for word_text in words:
            if len(line1 + word_text) < 50:
                line1 += word_text + " "
            else:
                line2 += word_text + " "
        
        cv2.putText(image_bgr, line1, (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        if line2:
            cv2.putText(image_bgr, line2, (40, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display score
        cv2.putText(image_bgr, f"Score: {score}/{total_questions}", (40, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Display user's typed word
        cv2.rectangle(image_bgr, (20, 200), (display_width - 20, 280), (40, 40, 40), -1)
        cv2.rectangle(image_bgr, (20, 200), (display_width - 20, 280), (255, 255, 255), 2)
        cv2.putText(image_bgr, f"Your Answer: {word}", (40, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

        # Display feedback message
        if game_state == "correct":
            cv2.rectangle(image_bgr, (display_width // 2 - 200, 300), 
                         (display_width // 2 + 200, 380), (0, 200, 0), -1)
            cv2.putText(image_bgr, "CORRECT!", (display_width // 2 - 120, 350), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        elif game_state == "wrong":
            cv2.rectangle(image_bgr, (display_width // 2 - 250, 300), 
                         (display_width // 2 + 250, 420), (0, 0, 200), -1)
            cv2.putText(image_bgr, "WRONG!", (display_width // 2 - 100, 340), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            cv2.putText(image_bgr, f"Answer: {current_answer}", (display_width // 2 - 200, 400), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Draw keyboard and buttons
        draw_keyboard(image_bgr)
        draw_special_buttons(image_bgr)

        # Hand detection
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    image_bgr, hand_landmarks,
                    connections=mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )

                # Get index finger tip
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_pixel = mp_drawing._normalized_to_pixel_coordinates(
                    index_finger_tip.x, index_finger_tip.y, display_width, display_height
                )

                if index_pixel and key_press_cooldown == 0:
                    current_x, current_y = index_pixel
                    
                    # Draw pointer
                    cv2.circle(image_bgr, (current_x, current_y), 15, (255, 0, 255), -1)

                    # Check for special button press
                    special_btn = detect_special_button(current_x, current_y)
                    if special_btn == "CLEAR":
                        word = ""
                        key_press_cooldown = cooldown_frames
                    elif special_btn == "SUBMIT" and game_state == "playing":
                        total_questions += 1
                        if check_answer(word, current_answer):
                            game_state = "correct"
                            score += 1
                        else:
                            game_state = "wrong"
                        key_press_cooldown = cooldown_frames
                    elif special_btn == "NEXT" and game_state in ["correct", "wrong"]:
                        # Get new riddle
                        current_riddle = get_new_riddle()
                        current_answer = current_riddle["answer"]
                        word = ""
                        game_state = "playing"
                        key_press_cooldown = cooldown_frames
                    
                    # Check for keyboard key press
                    if game_state == "playing":
                        key = detect_key(current_x, current_y)
                        if key and key != last_key_pressed:
                            word += key
                            last_key_pressed = key
                            key_press_cooldown = cooldown_frames

        # Reset last key if cooldown is active
        if key_press_cooldown == 0:
            last_key_pressed = None

        # Display instructions
        cv2.putText(image_bgr, "Point at keys to type | CLEAR to erase | SUBMIT to check answer", 
                   (30, display_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Display the output
        cv2.imshow("Word Guessing Game with Hand Gestures", image_bgr)

        # Break the loop if 'q' is pressed
        key_pressed = cv2.waitKey(10) & 0xFF
        if key_pressed == ord('q'):
            break

# Release video capture object and close display windows
video.release()
cv2.destroyAllWindows()