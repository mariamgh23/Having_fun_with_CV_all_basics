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

# Initialize Mediapipe Hand and Drawing Utils
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Desired display size
display_width = 1280
display_height = 720

# Game variables
board = [['' for _ in range(3)] for _ in range(3)]
player_symbol = None
computer_symbol = None
current_turn = 'player'
game_over = False
winner = None

# Grid settings
grid_size = 400
grid_offset_x = (display_width - grid_size) // 2
grid_offset_y = 100
cell_size = grid_size // 3

# Drawing variables
canvas = np.zeros((display_height, display_width, 3), dtype=np.uint8)
previous_x, previous_y = None, None
drawing_active = False

def draw_grid(frame):
    """Draw the Tic-Tac-Toe grid"""
    # Draw vertical lines
    for i in range(1, 3):
        x = grid_offset_x + i * cell_size
        cv2.line(frame, (x, grid_offset_y), (x, grid_offset_y + grid_size), (255, 255, 255), 3)
    
    # Draw horizontal lines
    for i in range(1, 3):
        y = grid_offset_y + i * cell_size
        cv2.line(frame, (grid_offset_x, y), (grid_offset_x + grid_size, y), (255, 255, 255), 3)
    
    # Draw border
    cv2.rectangle(frame, (grid_offset_x, grid_offset_y), 
                  (grid_offset_x + grid_size, grid_offset_y + grid_size), (255, 255, 255), 3)

def draw_perfect_symbol(canvas, row, col, symbol):
    """Draw a perfect X or O in a cell"""
    center_x = grid_offset_x + col * cell_size + cell_size // 2
    center_y = grid_offset_y + row * cell_size + cell_size // 2
    
    if symbol == 'X':
        # Draw perfect X
        offset = cell_size // 3
        cv2.line(canvas, (center_x - offset, center_y - offset), 
                 (center_x + offset, center_y + offset), (0, 0, 255), 5)
        cv2.line(canvas, (center_x + offset, center_y - offset), 
                 (center_x - offset, center_y + offset), (0, 0, 255), 5)
    elif symbol == 'O':
        # Draw perfect O
        radius = cell_size // 3
        cv2.circle(canvas, (center_x, center_y), radius, (0, 255, 0), 5)

def get_cell(x, y):
    """Convert pixel coordinates to grid cell"""
    if (grid_offset_x <= x <= grid_offset_x + grid_size and 
        grid_offset_y <= y <= grid_offset_y + grid_size):
        col = (x - grid_offset_x) // cell_size
        row = (y - grid_offset_y) // cell_size
        return row, col
    return None, None

def check_winner():
    """Check if there's a winner"""
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != '':
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != '':
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
        return board[0][2]
    
    # Check for draw
    if all(board[i][j] != '' for i in range(3) for j in range(3)):
        return 'Draw'
    
    return None

def computer_move():
    """Simple AI for computer move"""
    # Check if computer can win
    for i in range(3):
        for j in range(3):
            if board[i][j] == '':
                board[i][j] = computer_symbol
                if check_winner() == computer_symbol:
                    return
                board[i][j] = ''
    
    # Check if need to block player
    for i in range(3):
        for j in range(3):
            if board[i][j] == '':
                board[i][j] = player_symbol
                if check_winner() == player_symbol:
                    board[i][j] = computer_symbol
                    return
                board[i][j] = ''
    
    # Take center if available
    if board[1][1] == '':
        board[1][1] = computer_symbol
        return
    
    # Take a corner
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    random.shuffle(corners)
    for i, j in corners:
        if board[i][j] == '':
            board[i][j] = computer_symbol
            return
    
    # Take any available cell
    for i in range(3):
        for j in range(3):
            if board[i][j] == '':
                board[i][j] = computer_symbol
                return

def clear_cell_on_canvas(row, col):
    """Clear a cell on the canvas"""
    cell_x = grid_offset_x + col * cell_size
    cell_y = grid_offset_y + row * cell_size
    # Clear the cell area but keep the grid
    cv2.rectangle(canvas, (cell_x + 5, cell_y + 5), 
                 (cell_x + cell_size - 5, cell_y + cell_size - 5), (0, 0, 0), -1)

def reset_game():
    """Reset the game"""
    global board, current_turn, game_over, winner, player_symbol, computer_symbol, canvas, previous_x, previous_y
    board = [['' for _ in range(3)] for _ in range(3)]
    current_turn = 'player'
    game_over = False
    winner = None
    player_symbol = None
    computer_symbol = None
    canvas = np.zeros((display_height, display_width, 3), dtype=np.uint8)
    previous_x, previous_y = None, None

# Initialize video capture
video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, display_width)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, display_height)

# Initialize the Hand Tracker
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    
    # Symbol selection buttons
    button_width = 150
    button_height = 60
    x_button_pos = (display_width // 2 - button_width - 20, 20)
    o_button_pos = (display_width // 2 + 20, 20)
    
    # Track which cell we're currently in
    current_cell = None

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

        # If player hasn't chosen symbol yet
        if player_symbol is None:
            cv2.putText(image_bgr, "Choose Your Symbol:", (display_width // 2 - 150, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Draw X button
            cv2.rectangle(image_bgr, x_button_pos, 
                         (x_button_pos[0] + button_width, x_button_pos[1] + button_height), 
                         (0, 0, 255), -1)
            cv2.putText(image_bgr, "X", (x_button_pos[0] + 60, x_button_pos[1] + 45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            
            # Draw O button
            cv2.rectangle(image_bgr, o_button_pos, 
                         (o_button_pos[0] + button_width, o_button_pos[1] + button_height), 
                         (0, 255, 0), -1)
            cv2.putText(image_bgr, "O", (o_button_pos[0] + 60, o_button_pos[1] + 45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            
            # Check for hand pointing at buttons
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    pixel_coordinates = mp_drawing._normalized_to_pixel_coordinates(
                        index_finger_tip.x, index_finger_tip.y, display_width, display_height
                    )
                    
                    if pixel_coordinates:
                        x, y = pixel_coordinates
                        cv2.circle(image_bgr, (x, y), 10, (255, 0, 255), -1)
                        
                        # Check X button
                        if (x_button_pos[0] <= x <= x_button_pos[0] + button_width and 
                            x_button_pos[1] <= y <= x_button_pos[1] + button_height):
                            player_symbol = 'X'
                            computer_symbol = 'O'
                        
                        # Check O button
                        if (o_button_pos[0] <= x <= o_button_pos[0] + button_width and 
                            o_button_pos[1] <= y <= o_button_pos[1] + button_height):
                            player_symbol = 'O'
                            computer_symbol = 'X'
        
        else:
            # Draw the game grid on canvas
            draw_grid(canvas)
            
            # Display current turn
            if not game_over:
                turn_text = f"Your Turn - Draw {player_symbol}" if current_turn == 'player' else f"Computer's Turn ({computer_symbol})"
                cv2.putText(image_bgr, turn_text, (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Handle hand detection for player's turn
            if results.multi_hand_landmarks and current_turn == 'player' and not game_over:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        image_bgr, hand_landmarks,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=5),
                        connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
                    
                    # Get index finger tip
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    pixel_coordinates = mp_drawing._normalized_to_pixel_coordinates(
                        index_finger_tip.x, index_finger_tip.y, display_width, display_height
                    )
                    
                    if pixel_coordinates:
                        x, y = pixel_coordinates
                        
                        # Get cell position
                        row, col = get_cell(x, y)
                        
                        if row is not None and col is not None:
                            # Highlight the cell
                            cell_x = grid_offset_x + col * cell_size
                            cell_y = grid_offset_y + row * cell_size
                            cv2.rectangle(image_bgr, (cell_x, cell_y), 
                                        (cell_x + cell_size, cell_y + cell_size), 
                                        (255, 255, 0), 2)
                            
                            # Check if entering a new cell
                            if current_cell != (row, col):
                                current_cell = (row, col)
                                previous_x, previous_y = None, None
                            
                            # Draw if cell is empty
                            if board[row][col] == '':
                                # Set drawing color based on player symbol
                                if player_symbol == 'X':
                                    draw_color = (0, 0, 255)  # Red for X
                                else:
                                    draw_color = (0, 255, 0)  # Green for O
                                
                                # Draw on canvas with index finger
                                if previous_x is not None and previous_y is not None:
                                    cv2.line(canvas, (previous_x, previous_y), (x, y), draw_color, 5)
                                
                                previous_x, previous_y = x, y
                        else:
                            previous_x, previous_y = None, None
                            current_cell = None
            else:
                previous_x, previous_y = None, None
                current_cell = None
            
            # Overlay the canvas on the video feed
            final_output = cv2.addWeighted(image_bgr, 1.0, canvas, 1.0, 0)
            
            # Computer's turn
            if current_turn == 'computer' and not game_over:
                cv2.imshow("Tic-Tac-Toe with Hand Gestures", final_output)
                cv2.waitKey(500)  # Delay for visual effect
                computer_move()
                
                # Draw computer's perfect symbol on canvas
                for i in range(3):
                    for j in range(3):
                        if board[i][j] == computer_symbol:
                            # Find the newly placed symbol
                            draw_perfect_symbol(canvas, i, j, computer_symbol)
                
                winner = check_winner()
                if winner:
                    game_over = True
                else:
                    current_turn = 'player'
            
            # Display winner
            if game_over:
                if winner == 'Draw':
                    result_text = "It's a Draw!"
                    color = (255, 255, 0)
                elif winner == player_symbol:
                    result_text = "You Win!"
                    color = (0, 255, 0)
                else:
                    result_text = "Computer Wins!"
                    color = (0, 0, 255)
                
                # Draw semi-transparent background for winner text
                cv2.rectangle(final_output, (display_width // 2 - 200, display_height - 150), 
                             (display_width // 2 + 200, display_height - 50), (0, 0, 0), -1)
                cv2.putText(final_output, result_text, (display_width // 2 - 150, display_height - 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
                cv2.putText(final_output, "Press 'R' to Reset", (display_width // 2 - 150, display_height - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Display instructions
            cv2.putText(final_output, "Draw in empty cells | Press 'C' to clear cell | 'Space' to confirm move", 
                       (10, display_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(final_output, "Press 'Q' to Quit | 'R' to Reset", (10, display_height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # Display the output
            cv2.imshow("Tic-Tac-Toe with Hand Gestures", final_output)
        
        # Only show this screen if not in game yet
        if player_symbol is None:
            cv2.imshow("Tic-Tac-Toe with Hand Gestures", image_bgr)

        # Handle key presses
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            reset_game()
        elif key == ord(' ') and current_turn == 'player' and not game_over and current_cell is not None:
            # Confirm move with spacebar - transform drawing to perfect symbol
            row, col = current_cell
            if board[row][col] == '':
                # Clear the hand-drawn content in this cell
                clear_cell_on_canvas(row, col)
                
                # Draw perfect symbol
                draw_perfect_symbol(canvas, row, col, player_symbol)
                
                # Update board
                board[row][col] = player_symbol
                current_turn = 'computer'
                winner = check_winner()
                if winner:
                    game_over = True
                previous_x, previous_y = None, None
                current_cell = None
        elif key == ord('c') and current_turn == 'player' and not game_over and current_cell is not None:
            # Clear current cell with 'c' key
            row, col = current_cell
            if board[row][col] == '':
                clear_cell_on_canvas(row, col)
                previous_x, previous_y = None, None

# Release video capture object and close display windows
video.release()
cv2.destroyAllWindows()