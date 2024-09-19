import cv2
import mediapipe as mp
import pygame
import sys
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import numpy as np

# Initialize MediaPipe Hand solution
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Virtual Smart Board')

# Create surfaces
background_surface = pygame.Surface((screen_width, screen_height))
drawing_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)  # Use SRCALPHA for transparency
indicator_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

# Fill the background surface with white (or black based on the initial board state)
background_color = (255, 255, 255)  # White for the initial board
background_surface.fill(background_color)

# Colors
colors = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0)
}

current_color = colors["black"]

# Define button rectangles
button_rects = {
    "paint": pygame.Rect(10, 10, 80, 40),
    "clear": pygame.Rect(100, 10, 80, 40),
    "black": pygame.Rect(190, 10, 40, 40),
    "white": pygame.Rect(240, 10, 40, 40),
    "red": pygame.Rect(290, 10, 40, 40),
    "green": pygame.Rect(340, 10, 40, 40),
    "blue": pygame.Rect(390, 10, 40, 40),
    "yellow": pygame.Rect(440, 10, 40, 40),
    "erase": pygame.Rect(490, 10, 80, 40),
    "board": pygame.Rect(10, screen_height - 50, 80, 40)  # Board button moved to bottom left
}

# Variables for drawing
drawing = False
prev_x, prev_y = None, None
erase_mode = False
shift_pressed = False

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initial board state (True for whiteboard, False for blackboard)
is_whiteboard = True  # Default is whiteboard

def save_drawing(surface):
    """Save the current drawing surface as an image file."""
    pygame.image.save(surface, "drawing.png")
    print("Drawing saved as drawing.png")

def draw_buttons(surface):
    """Draw the buttons on the Pygame surface."""
    pygame.draw.rect(surface, (200, 200, 200), button_rects["paint"])
    pygame.draw.rect(surface, (200, 200, 200), button_rects["clear"])
    pygame.draw.rect(surface, colors["black"], button_rects["black"])
    pygame.draw.rect(surface, colors["white"], button_rects["white"])
    pygame.draw.rect(surface, colors["red"], button_rects["red"])
    pygame.draw.rect(surface, colors["green"], button_rects["green"])
    pygame.draw.rect(surface, colors["blue"], button_rects["blue"])
    pygame.draw.rect(surface, colors["yellow"], button_rects["yellow"])
    pygame.draw.rect(surface, (150, 150, 150), button_rects["erase"])
    pygame.draw.rect(surface, (200, 200, 200), button_rects["board"])  # Draw board color toggle button

    font = pygame.font.Font(None, 36)
    text = font.render('Paint', True, (0, 0, 0))
    surface.blit(text, (15, 15))
    text = font.render('Clear', True, (0, 0, 0))
    surface.blit(text, (105, 15))
    text = font.render('Erase', True, (0, 0, 0))
    surface.blit(text, (495, 15))
    text = font.render('Board', True, (0, 0, 0))
    surface.blit(text, (15, screen_height - 45))

def toggle_board_color():
    global is_whiteboard, background_surface, drawing_surface, current_color
    is_whiteboard = not is_whiteboard
    if is_whiteboard:
        background_surface.fill((255, 255, 255))
        current_color = colors["black"]
    else:
        background_surface.fill((0, 0, 0))
        current_color = colors["white"]
    # Refill the drawing surface to maintain transparency effect
    drawing_surface.fill((0, 0, 0, 0))  # Reset to transparent

def load_image():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
    if file_path:
        image = Image.open(file_path)
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    return None

def is_close(p1, p2, threshold=20):
    """Check if two points are close to each other within a given threshold."""
    distance = np.linalg.norm(np.array(p1) - np.array(p2))
    return distance < threshold

# Main loop
running = True
loaded_image = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and shift_pressed:  # Shift + Q
                erase_mode = False
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                shift_pressed = True
            elif event.key == pygame.K_q:  # Quit and save drawing
                save_drawing(drawing_surface)
                running = False
            elif event.key == pygame.K_d:  # Start drawing when 'd' is pressed
                drawing = True
            elif event.key == pygame.K_s:  # Stop drawing when 's' is pressed
                drawing = False
            elif event.key == pygame.K_o:  # Press 'O' to open an image
                loaded_image = load_image()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                shift_pressed = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if button_rects["paint"].collidepoint(mouse_pos):
                drawing = True
                erase_mode = False
            elif button_rects["clear"].collidepoint(mouse_pos):
                drawing_surface.fill((0, 0, 0, 0))  # Clear only the drawing surface
            elif button_rects["black"].collidepoint(mouse_pos):
                current_color = colors["black"]
            elif button_rects["white"].collidepoint(mouse_pos):
                current_color = colors["white"]
            elif button_rects["red"].collidepoint(mouse_pos):
                current_color = colors["red"]
            elif button_rects["green"].collidepoint(mouse_pos):
                current_color = colors["green"]
            elif button_rects["blue"].collidepoint(mouse_pos):
                current_color = colors["blue"]
            elif button_rects["yellow"].collidepoint(mouse_pos):
                current_color = colors["yellow"]
            elif button_rects["erase"].collidepoint(mouse_pos):
                erase_mode = not erase_mode
            elif button_rects["board"].collidepoint(mouse_pos):
                toggle_board_color()

    success, image = cap.read()
    if not success:
        continue

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)
    
    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image and detect hands
    results = hands.process(image_rgb)
    
    # Draw buttons
    draw_buttons(drawing_surface)

    # Clear the indicator surface
    indicator_surface.fill((0, 0, 0, 0))  # Transparent background

    # Draw hand landmarks and connections
    hand_detected = False
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            hand_detected = True
            # Extract index finger tip coordinates (landmark 8) and thumb tip coordinates (landmark 4)
            index_finger_tip = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]
            h, w, _ = image.shape
            cx_index, cy_index = int(index_finger_tip.x * screen_width), int(index_finger_tip.y * screen_height)
            cx_thumb, cy_thumb = int(thumb_tip.x * screen_width), int(thumb_tip.y * screen_height)
            
            # Draw green circles at the index finger tip and thumb tip on the indicator surface
            pygame.draw.circle(indicator_surface, (0, 255, 0), (cx_index, cy_index), 10)
            pygame.draw.circle(indicator_surface, (0, 255, 0), (cx_thumb, cy_thumb), 10)

            # Check for button presses
            if is_close((cx_index, cy_index), (cx_thumb, cy_thumb)):
                if button_rects["clear"].collidepoint((cx_index, cy_index)):
                    drawing_surface.fill((0, 0, 0, 0))  # Clear only the drawing surface
                elif button_rects["black"].collidepoint((cx_index, cy_index)):
                    current_color = colors["black"]
                elif button_rects["white"].collidepoint((cx_index, cy_index)):
                    current_color = colors["white"]
                elif button_rects["red"].collidepoint((cx_index, cy_index)):
                    current_color = colors["red"]
                elif button_rects["green"].collidepoint((cx_index, cy_index)):
                    current_color = colors["green"]
                elif button_rects["blue"].collidepoint((cx_index, cy_index)):
                    current_color = colors["blue"]
                elif button_rects["yellow"].collidepoint((cx_index, cy_index)):
                    current_color = colors["yellow"]
                elif button_rects["erase"].collidepoint((cx_index, cy_index)):
                    erase_mode = not erase_mode
                elif button_rects["board"].collidepoint((cx_index, cy_index)):
                    toggle_board_color()

                # Start drawing or erasing if the index finger and thumb are close
                if drawing:
                    if prev_x is not None and prev_y is not None:
                        if erase_mode:
                            pygame.draw.circle(drawing_surface, (0, 0, 0, 0), (cx_index, cy_index), 15)  # Erase with transparency
                        else:
                            pygame.draw.line(drawing_surface, current_color, (prev_x, prev_y), (cx_index, cy_index), 5)

            # Update previous coordinates
            prev_x, prev_y = cx_index, cy_index

    # Display the surfaces on the main screen
    screen.blit(background_surface, (0, 0))  # Draw the background surface
    screen.blit(drawing_surface, (0, 0))  # Draw the main drawing surface
    screen.blit(indicator_surface, (0, 0))  # Draw the indicator surface on top

    # Draw the loaded image
    if loaded_image:
        screen.blit(loaded_image, (0, 0))

    pygame.display.flip()

    # Reset previous coordinates if not drawing
    if not drawing:
        prev_x, prev_y = None, None

# Release resources
cap.release()
hands.close()
pygame.quit()
sys.exit()
