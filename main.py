import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import random
import time

correctionValue = 2.1
directions = ['U', 'D', 'L', 'R']
max_rounds = 3

# 얼굴 메시 감지기 초기화
detector = FaceMeshDetector(maxFaces=1)

# 웹캠에서 비디오 캡처
cap = cv2.VideoCapture(0)

# 게임 상태
def reset_game():
    global current_direction, start_time, round_count, success_count, game_state, user_wins
    current_direction = random.choice(directions)
    start_time = time.time()
    round_count = 0
    success_count = 0
    game_state = 'playing'
    user_wins = 0

reset_game()

while True:
    # 비디오 프레임 읽기
    success, img = cap.read()
    if not success:
        break

    # 좌우 반전
    img = cv2.flip(img, 1)

    # 얼굴 메시 감지
    img, faces = detector.findFaceMesh(img, draw=True)

    # 현재 시간과 경과 시간 계산
    current_time = time.time()
    elapsed_time = current_time - start_time

    if game_state == 'playing':
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

                # 눈과 코의 위치로부터 얼굴의 방향 추정
                nose_to_left_eye = (left_eye[0] - nose_tip[0], left_eye[1] - nose_tip[1])
                nose_to_right_eye = (right_eye[0] - nose_tip[0], right_eye[1] - nose_tip[1])

                # 벡터의 길이 계산
                left_eye_distance = (nose_to_left_eye[0]**2 + nose_to_left_eye[1]**2)**0.5
                right_eye_distance = (nose_to_right_eye[0]**2 + nose_to_right_eye[1]**2)**0.5

                # 방향 판단
                detected_direction = 'Def'
                if left_eye_distance > right_eye_distance * correctionValue:
                    detected_direction = 'L'
                elif right_eye_distance > left_eye_distance * correctionValue:
                    detected_direction = 'R'
                else:
                    detected_direction = 'Def'
                
                if detected_direction == current_direction:
                    user_wins += 1
                    cv2.putText(img, 'Correct!', (img.shape[1] // 2 - 100, img.shape[0] // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)
                else:
                    cv2.putText(img, 'Wrong!', (img.shape[1] // 2 - 100, img.shape[0] // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)

                cv2.imshow("Face Direction", img)
                cv2.waitKey(1000)  # 1초 동안 화면 정지

                round_count += 1

                if round_count >= max_rounds:
                    if user_wins == max_rounds:
                        game_state = 'win'
                    else:
                        game_state = 'reset'
                else:
                    # 새로운 방향과 카운트다운 시간 초기화
                    reset_game()
            else:
                game_state = 'reset'

    if game_state == 'win':
        cv2.putText(img, f'Win! Total Wins: {user_wins}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    elif game_state == 'reset':
        cv2.putText(img, 'Try Again! Press R to Restart', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(img, f'Wins: {user_wins}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        # 재시작 대기
        key = cv2.waitKey(0)
        if key == ord('q'):
            break
        elif key == ord('r'):
            reset_game()
            game_state = 'playing'

    # 결과 이미지 표시
    cv2.imshow("Face Direction", img)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 웹캠 및 창 자원 해제
cap.release()
cv2.destroyAllWindows()
