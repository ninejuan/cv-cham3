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
total_streak_needed = 3  # 3번 연속 승리 필요

# 얼굴 메시 감지기 초기화
detector = FaceMeshDetector(maxFaces=1)

# 웹캠에서 비디오 캡처
cap = cv2.VideoCapture(0)

# 게임 상태
def reset_game():
    global current_direction, start_time, round_count, game_state, user_wins, correct_streak, fail_streak
    current_direction = random.choice(directions)
    start_time = time.time()
    round_count = 0
    game_state = 'main_screen'
    user_wins = 0
    correct_streak = 0
    fail_streak = 0  # 새 변수 추가

def show_main_screen():
    global img
    img = np.zeros((480, 640, 3), dtype=np.uint8)  # 640x480 크기의 검은색 이미지를 생성합니다.
    img[:] = (128, 128, 128)  # 회색 배경
    cv2.putText(img, 'Cham Cham Cham', (img.shape[1] // 2 - 200, img.shape[0] // 2 - 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 0), 3, cv2.LINE_AA)
    cv2.putText(img, "Press 'S' to start game.", (img.shape[1] // 2 - 200, img.shape[0] // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, "Press 'Q' to quit game.", (img.shape[1] // 2 - 200, img.shape[0] // 2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow("Face Direction", img)

reset_game()
show_main_screen()

while True:
    # 비디오 프레임 읽기
    success, frame = cap.read()
    if not success:
        break

    # 좌우 반전
    img = cv2.flip(frame, 1)

    # 게임 상태에 따라 처리
    if game_state == 'main_screen':
        show_main_screen()
        key = cv2.waitKey(1)
        if key == ord('s'):
            reset_game()
            game_state = 'playing'
        elif key == ord('q'):
            break

    elif game_state == 'playing':
        # 얼굴 메시 감지
        img, faces = detector.findFaceMesh(img, draw=True)

        # 현재 시간과 경과 시간 계산
        current_time = time.time()
        elapsed_time = current_time - start_time

        # 카운트다운 표시
        remaining_time = max(0, int(5 - elapsed_time))
        cv2.putText(img, f'Time left: {remaining_time}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        if elapsed_time >= 5:
            # 방향 지시와 카운트다운 시간 초과 후
            if faces:
                # 첫 번째 얼굴에 대한 정보 얻기
                face = faces[0]

                # 코와 눈의 좌표 얻기
                nose_tip = face[4]
                left_eye = face[33]
                right_eye = face[263]

                # 코와 눈 사이의 거리 계산
                left_eye_distance = np.sqrt((left_eye[0] - nose_tip[0]) ** 2 + (left_eye[1] - nose_tip[1]) ** 2)
                right_eye_distance = np.sqrt((right_eye[0] - nose_tip[0]) ** 2 + (right_eye[1] - nose_tip[1]) ** 2)

                # 방향 판단
                detected_direction = 'Not Moved'
                if right_eye_distance > left_eye_distance * correctionValue:
                    detected_direction = 'Left'
                elif left_eye_distance > right_eye_distance * correctionValue:
                    detected_direction = 'Right'
                else:
                    detected_direction = 'Not Moved'

                # 결과 표시
                if detected_direction != current_direction:
                    correct_streak += 1
                    cv2.putText(img, 'Correct!', (img.shape[1] // 2 - 100, img.shape[0] // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)
                else:
                    correct_streak = 0
                    fail_streak += 1  # 실패 횟수 증가
                    cv2.putText(img, 'Wrong!', (img.shape[1] // 2 - 100, img.shape[0] // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)

                cv2.putText(img, f'Computer: {current_direction}', (img.shape[1] // 2 - 150, img.shape[0] // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if detected_direction != current_direction else (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(img, f'You: {detected_direction}', (img.shape[1] // 2 - 150, img.shape[0] // 2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if detected_direction != current_direction else (0, 0, 255), 2, cv2.LINE_AA)
                
                cv2.imshow("Face Direction", img)
                cv2.waitKey(2000)  # 2초 동안 화면 정지

                if correct_streak >= correct_streak_needed:
                    user_wins += 1
                    correct_streak = 0  # 연속 승리 조건 리셋
                    if user_wins >= total_streak_needed:
                        game_state = 'win'
                    else:
                       reset_game()
                round_count += 1
                if round_count >= max_rounds:
                    if fail_streak > 0:  # 실패 횟수 체크
                        game_state = 'fail'
                    else:
                        reset_game()
            else:
                game_state = 'reset'

    elif game_state == 'win':
        cv2.putText(img, 'You Win!', (img.shape[1] // 2 - 100, img.shape[0] // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)
        cv2.putText(img, 'Returning to main screen...', (img.shape[1] // 2 - 200, img.shape[0] // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Face Direction", img)
        cv2.waitKey(10000)  # 10초 동안 화면 정지
        game_state = 'main_screen'

    elif game_state == 'fail':
        cv2.putText(img, 'Fail!', (img.shape[1] // 2 - 100, img.shape[0] // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.putText(img, 'Returning to main screen...', (img.shape[1] // 2 - 200, img.shape[0] // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("Face Direction", img)
        cv2.waitKey(5000)  # 5초 동안 화면 정지
        game_state = 'main_screen'

    elif game_state == 'reset':
        user_wins = 0
        cv2.putText(img, 'Resetting...', (img.shape[1] // 2 - 100, img.shape[0] // 2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3, cv2.LINE_AA)
        cv2.imshow("Face Direction", img)
        cv2.waitKey(10000)  # 10초 동안 화면 정지
        game_state = 'main_screen'

    # 결과 이미지 표시
    cv2.imshow("Face Direction", img)

    # 종료 또는 메인 페이지로 돌아가기
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# 웹캠 및 창 자원 해제
cap.release()
cv2.destroyAllWindows()
