import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector

correctionValue = 2.1

# 얼굴 메시 감지기 초기화
detector = FaceMeshDetector(maxFaces=1)

# 웹캠에서 비디오 캡처
cap = cv2.VideoCapture(0)

while True:
    # 비디오 프레임 읽기
    success, img = cap.read()
    if not success:
        break

    # 얼굴 메시 감지
    img, faces = detector.findFaceMesh(img, draw=True)

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
        if left_eye_distance > right_eye_distance * correctionValue:
            direction = 'L'
        elif right_eye_distance > left_eye_distance * correctionValue:
            direction = 'R'
        else:
            direction = 'Def'

        # 얼굴 방향 표시
        cv2.putText(img, f'Face Direction: {direction}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # 결과 이미지 표시
    cv2.imshow("Face Direction", img)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 웹캠 및 창 자원 해제
cap.release()
cv2.destroyAllWindows()
