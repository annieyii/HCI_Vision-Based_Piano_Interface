# utils/hand_processing.py
# 原本是utils.py

import cv2
import numpy as np

def smooth_value(history, value, max_len=5):
    history.append(value)
    if len(history) > max_len:
        history.pop(0)
    return float(np.mean(history))

def extract_finger_pixels(left_hand, right_hand, frame_w, frame_h):
    fingers = []
    tip_ids = [4, 8, 12, 16, 20]  # 10指指尖點

    if left_hand is not None:
        for tid in tip_ids:
            x = int(left_hand[tid][0] * frame_w)
            y = int(left_hand[tid][1] * frame_h)
            z = left_hand[tid][2]
            fingers.append((x, y, z))

    if right_hand is not None:
        for tid in tip_ids:
            x = int(right_hand[tid][0] * frame_w)
            y = int(right_hand[tid][1] * frame_h)
            z = right_hand[tid][2]
            fingers.append((x, y, z))

    return fingers

# 畫手部 landmark 點 (debug 用)
def draw_hand_landmarks(frame, hand):
    if hand is None:
        return

    h, w, _ = frame.shape
    for lm in hand:
        cx = int(lm[0] * w)
        cy = int(lm[1] * h)
        cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
