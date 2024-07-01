import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def is_waving(hand_landmarks, pose_landmarks, prev_wrist_y):
    wrist = hand_landmarks[0]
    index_tip = hand_landmarks[8]
    thumb_tip = hand_landmarks[4]

    # Captura a distância entre o pulso e o pescoço
    neck = pose_landmarks[11]
    shoulder = pose_landmarks[12]

    wrist_above_shoulder = wrist.y < shoulder.y
    wrist_stable = abs(wrist.y - prev_wrist_y) < 0.05
    wrist_moving = abs(wrist.y - neck.y) < 0.2

    return wrist_above_shoulder and wrist_stable and wrist_moving

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands, mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:
    prev_wrist_y = None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        hand_results = hands.process(image)
        pose_results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if hand_results.multi_hand_landmarks and pose_results.pose_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0].landmark
            pose_landmarks = pose_results.pose_landmarks.landmark

            if prev_wrist_y is None:
                prev_wrist_y = hand_landmarks[0].y

            if is_waving(hand_landmarks, pose_landmarks, prev_wrist_y):
                cv2.putText(image, 'Acenando!', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            prev_wrist_y = hand_landmarks[0].y

            mp_drawing.draw_landmarks(
                image, hand_results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(
                image, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow('Mediapipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
