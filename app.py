
import mediapipe as mp
import numpy as np
import cv2
import os
import random
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Paths
MODEL_PATH = 'rock_paper_scissors.task'
VIDEO_PATH = 'Assets/playing_video.mp4'
IMG_PATHS = {
    'rock': 'Assets/Rock.png',
    'paper': 'Assets/Paper.png',
    'scissors': 'Assets/Scissors.png'
}

# Check files
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
if not os.path.exists(VIDEO_PATH):
    raise FileNotFoundError(f"Video file not found: {VIDEO_PATH}")
for img in IMG_PATHS.values():
    if not os.path.exists(img):
        raise FileNotFoundError(f"Image file not found: {img}")

# Load images
images = {k: cv2.imread(v) for k, v in IMG_PATHS.items()}

# Setup model
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=1)
recognizer = vision.GestureRecognizer.create_from_options(options)


# Setup video and webcam
video = cv2.VideoCapture(VIDEO_PATH)
cap = cv2.VideoCapture(0)
FRAME_W, FRAME_H = 1280, 720
# Ratio: 40% for video/image, 60% for cam view
LEFT_W = int(FRAME_W * 0.4)
RIGHT_W = FRAME_W - LEFT_W
cap.set(3, RIGHT_W)
cap.set(4, FRAME_H)

def get_gesture_label(result):
    if result.gestures:
        gesture = result.gestures[0][0]
        label = gesture.category_name.lower()
        if label in ['rock', 'paper', 'scissors']:
            return label
    return None

def decide_winner(user, computer):
    if user == computer:
        return 'Draw'
    if (user == 'rock' and computer == 'scissors') or \
       (user == 'paper' and computer == 'rock') or \
       (user == 'scissors' and computer == 'paper'):
        return 'User'
    return 'Computer'

def overlay_result(frame, winner):
    text = ''
    color = (0,255,0) if winner == 'User' else (0,0,255)
    if winner == 'Draw':
        text = 'Draw!'
        color = (255,255,0)
    elif winner == 'User':
        text = 'You Win!'
    else:
        text = 'You Lose!'
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.2
    thickness = 6
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = (frame.shape[1] - text_size[0]) // 2
    y = 80 + text_size[1] // 2
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    return frame

def resize_left(img):
    # Resize video/image to left side width
    return cv2.resize(img, (LEFT_W, FRAME_H), interpolation=cv2.INTER_AREA)

def resize_right(img):
    # Resize cam view to right side width
    return cv2.resize(img, (RIGHT_W, FRAME_H), interpolation=cv2.INTER_AREA)

def draw_countdown(frame, seconds_left):
    # Overlay countdown timer on frame
    timer_text = f"{seconds_left}"
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 2.5
    thickness = 5
    color = (0, 255, 255)
    text_size, _ = cv2.getTextSize(timer_text, font, font_scale, thickness)
    # Shift timer to left
    x = 40
    y = 80 + text_size[1] // 2
    cv2.putText(frame, timer_text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    return frame

def draw_prompt(frame, msg):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 3
    color = (0, 0, 255)
    text_size, _ = cv2.getTextSize(msg, font, font_scale, thickness)
    x = (frame.shape[1] - text_size[0]) // 2
    y = frame.shape[0] - 40
    cv2.putText(frame, msg, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    return frame

def main():
    while True:
        # --- Play/Buffer period ---
        # Time control for play/buffer period
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        buffer_start = time.time()
        buffer_duration = 5  # seconds
        user_choice = None
        computer_choice = None
        gesture_detected = False
        freeze_frame = None

        # Computer chooses just before gesture input
        computer_choice = random.choice(['rock', 'paper', 'scissors'])
        img_comp = resize_left(images[computer_choice])

        # Show video/cam split, show countdown, and detect gesture exactly when countdown ends
        gesture_frame = None
        while True:
            elapsed = time.time() - buffer_start
            seconds_left = max(0, int(buffer_duration - elapsed) + 1)
            if elapsed >= buffer_duration:
                # Capture the frame at the moment countdown ends
                ret_cam, frame_cam = cap.read()
                if not ret_cam:
                    break
                frame_cam = resize_right(frame_cam)
                frame_cam = cv2.flip(frame_cam, 1)  # Flip cam view horizontally
                gesture_frame = frame_cam.copy()
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(gesture_frame, cv2.COLOR_BGR2RGB))
                result = recognizer.recognize(mp_image)
                label = get_gesture_label(result)
                if label:
                    user_choice = label
                    gesture_detected = True
                    freeze_frame = gesture_frame.copy()
                break
            ret_vid, frame_vid = video.read()
            ret_cam, frame_cam = cap.read()
            if not ret_vid:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_vid, frame_vid = video.read()
            if not ret_cam:
                continue
            frame_vid = resize_left(frame_vid)
            frame_cam = resize_right(frame_cam)
            frame_cam = cv2.flip(frame_cam, 1)  # Flip cam view horizontally

            # Show countdown timer
            combined = np.hstack((frame_vid, frame_cam))
            combined = draw_countdown(combined, seconds_left)
            if not gesture_detected:
                combined = draw_prompt(combined, "Show your gesture!")
            cv2.imshow('Rock Paper Scissors', combined)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                cap.release()
                video.release()
                cv2.destroyAllWindows()
                return

        # --- Decide winner ---
        # Only show result if gesture detected
        if gesture_detected:
            winner = decide_winner(user_choice, computer_choice)
            # --- Result appearance period ---
            # Time control for result appearance
            result_overlay_time = time.time() + 3  # seconds
            while time.time() < result_overlay_time:
                # Show computer image and frozen cam view with result overlay
                frame_cam = freeze_frame
                combined = np.hstack((img_comp, frame_cam))
                combined = overlay_result(combined, winner)
                cv2.imshow('Rock Paper Scissors', combined)
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord('q'):
                    cap.release()
                    video.release()
                    cv2.destroyAllWindows()
                    return
        else:
            # Show message for no gesture detected
            result_overlay_time = time.time() + 3  # seconds
            while time.time() < result_overlay_time:
                ret_cam, frame_cam = cap.read()
                if not ret_cam:
                    continue
                frame_cam = resize_right(frame_cam)
                frame_cam = cv2.flip(frame_cam, 1)  # Flip cam view horizontally
                combined = np.hstack((img_comp, frame_cam))
                combined = draw_prompt(combined, "No gesture detected! Please try.")
                cv2.imshow('Rock Paper Scissors', combined)
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord('q'):
                    cap.release()
                    video.release()
                    cv2.destroyAllWindows()
                    return
if __name__ == '__main__':
    main()