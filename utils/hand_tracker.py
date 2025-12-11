# utils/hand_tracker.py
import cv2
import mediapipe as mp
import numpy as np
import time

from .hand_processing import smooth_value

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            model_complexity=1
        )

        # 桌面校正
        self.table_z = None
        self.table_y_pixel = None
        self.table_locked = False
        self.table_lock_time = None

        self.table_rect = None
        
        # smoothing
        self.z_history_L = []
        self.z_history_R = []

    # Mediapipe 手部偵測 （預設食指位置的y值為桌面高度）
    def detect(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        left_hand = None
        right_hand = None
        left_z = None
        right_z = None

        handed_list = []

        if results.multi_hand_landmarks:
            for lm, handed in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    lm,
                    self.mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )
                pts = np.array([(p.x, p.y, p.z) for p in lm.landmark])
                label = handed.classification[0].label
                handed_list.append(label)

                if label == "Left":
                    left_hand = pts
                    left_z = pts[8][2] 
                else:
                    right_hand = pts
                    right_z = pts[8][2]

        return left_hand, right_hand, left_z, right_z, handed_list


    def update_table_calibration(self, left_hand, right_hand, frame_h):
        if self.table_locked: return

        finger = None
        if left_hand is not None:
            finger = left_hand[8] # 食指
            side = "Left"
        elif right_hand is not None:
            finger = right_hand[8] # 食指
            side = "Right"
        else:
            self.table_lock_time = None
            return

        index_z = finger[2]
        index_y = finger[1]

        if side == "Left":
            z_smooth = smooth_value(self.z_history_L, index_z)
        else:
            z_smooth = smooth_value(self.z_history_R, index_z)

        if self.table_lock_time is None:
            self.table_lock_time = time.time()
            return

        if time.time() - self.table_lock_time >= 1.5:
            self.table_z = z_smooth
            self.table_y_pixel = int(index_y * frame_h)
            self.table_locked = True

            print(f"Table calibration finished")


    def is_hand_up(self, z_val):
        if self.table_z is None:
            return False
        return z_val < self.table_z - 0.015  

    # 依掌寬決定用於校正琴鍵寬度的是哪隻手
    def get_dominant(self, left_hand, right_hand):
        if left_hand is None and right_hand is None:
            return None
        if left_hand is None:
            return "Right"
        if right_hand is None:
            return "Left"

        lw = abs(left_hand[4][0] - left_hand[20][0])
        rw = abs(right_hand[4][0] - right_hand[20][0])

        return "Left" if lw > rw else "Right"
