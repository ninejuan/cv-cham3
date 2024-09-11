import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import random
import time
import numpy as np

correctionValue = 1.5
directions = ['Left', 'Right']
max_rounds = 3
correct_streak_needed = 3
fail_on_not_moved = False  # 'Not Moved' 상태에서 패배 여부를 제어하는 변수

# 얼굴 메시 감지기 초기화
detector = FaceMeshDetector(maxFaces=1)

# 웹캠에서 비디오 캡처
cap = cv2.VideoCapture(0)

# 텍스트를 화면 중앙에 배치하는 함수
def put_text_center(img, text, y_offset=0, font_scale=1, color=(255, 255, 255), thickness=2):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = (img.shape[0] + text_size[1]) // 2 + y_offset
    cv2.putText(img, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

# 게임 상태
def reset_game():
    global current_direction, start_time, round_count, game_state, correct_streak
    current_direction = random.choice(directions)
    start_time = time.time()
    round_count = 0
    game_state = 'main_screen'
    correct_streak = 0

def show_main_screen():
    global img
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (128, 128, 128)
    put_text_center(img, 'Cham Cham Cham', y_offset=-100, font_scale=1.4, color=(0, 255, 0), thickness=3)
    put_text_center(img, "Press 'S' to start game.", y_offset=0)
    put_text_center(img, "Press 'Q' to quit game.", y_offset=60)
    cv2.imshow("Face Direction", img)

def rgb2bgr(r, g, b):
    return (b, g, r)

def calcResultTextcolor(detected_direction, current_direction, isNotMovedAllowed):
    if detected_direction == current_direction:
        return rgb2bgr(255, 0, 0)
    else:
        if not isNotMovedAllowed:
            return rgb2bgr(0, 255, 0)
        else:
            return rgb2bgr(255, 0, 0)
            

reset_game()
show_main_screen()

while True:
    success, frame = cap.read()
    if not success:
        break

    img = cv2.flip(frame, 1)

    if game_state == 'main_screen':
        show_main_screen()
        key = cv2.waitKey(1)
        if key == ord('s'):
            reset_game()
            game_state = 'playing'
        elif key == ord('q'):
            break

    elif game_state == 'playing':
        img, faces = detector.findFaceMesh(img, draw=True)

        current_time = time.time()
        elapsed_time = current_time - start_time

        remaining_time = max(0, int(5 - elapsed_time))
        put_text_center(img, f'Time left: {remaining_time}', y_offset=-210, color=(0, 255, 0))
        put_text_center(img, f'Round: {round_count + 1}/{max_rounds}', y_offset=-170, color=(0, 255, 0))

        if elapsed_time >= 5:
            if faces:
                face = faces[0]
                nose_tip = face[4]
                left_eye = face[33]
                right_eye = face[263]

                left_eye_distance = np.sqrt((left_eye[0] - nose_tip[0]) ** 2 + (left_eye[1] - nose_tip[1]) ** 2)
                right_eye_distance = np.sqrt((right_eye[0] - nose_tip[0]) ** 2 + (right_eye[1] - nose_tip[1]) ** 2)

                detected_direction = 'Not Moved'
                if right_eye_distance > left_eye_distance * correctionValue:
                    detected_direction = 'Left'
                elif left_eye_distance > right_eye_distance * correctionValue:
                    detected_direction = 'Right'

                if detected_direction == 'Not Moved' and fail_on_not_moved:
                    game_state = 'fail'
                    put_text_center(img, 'Not Moved! You Lose!', y_offset=-30, font_scale=1.5, color=(0, 0, 255), thickness=3)
                elif detected_direction != current_direction:
                    correct_streak += 1
                    put_text_center(img, 'Correct!', y_offset=-30, font_scale=2, color=(0, 255, 0), thickness=3)
                else:
                    game_state = 'fail'
                    put_text_center(img, 'Wrong!', y_offset=-30, font_scale=2, color=(0, 0, 255), thickness=3)

                put_text_center(img, f'Computer: {current_direction}', y_offset=30, color=calcResultTextcolor(detected_direction, current_direction, fail_on_not_moved))
                put_text_center(img, f'You: {detected_direction}', y_offset=60, color=calcResultTextcolor(detected_direction, current_direction, fail_on_not_moved))
                
                cv2.imshow("Face Direction", img)
                cv2.waitKey(3000)

                if game_state != 'fail':
                    round_count += 1
                    if round_count >= max_rounds:
                        if correct_streak >= correct_streak_needed:
                            game_state = 'win'
                        else:
                            game_state = 'fail'
                    else:
                        current_direction = random.choice(directions)
                        start_time = time.time()

            else:
                game_state = 'reset'

    elif game_state == 'win':
        put_text_center(img, 'You Win!', y_offset=-60, font_scale=2, color=(0, 255, 0), thickness=3)
        put_text_center(img, 'Returning to main screen...')
        cv2.imshow("Face Direction", img)
        cv2.waitKey(10000)
        game_state = 'main_screen'

    elif game_state == 'fail':
        put_text_center(img, 'Game Over!', y_offset=-60, font_scale=2, color=(0, 0, 255), thickness=3)
        put_text_center(img, 'Returning to main screen...')
        cv2.imshow("Face Direction", img)
        cv2.waitKey(5000)
        game_state = 'main_screen'

    elif game_state == 'reset':
        put_text_center(img, 'Resetting...', y_offset=-30, font_scale=2, color=(0, 255, 255), thickness=3)
        cv2.imshow("Face Direction", img)
        cv2.waitKey(2000)
        reset_game()

    cv2.imshow("Face Direction", img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()