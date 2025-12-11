# utils/calibration.py
import cv2
import math
import numpy as np

def compute_hand_width(landmarks, W, H):
    """計算拇指 tip ~ 小指 tip 之間距離。"""
    thumb = landmarks.landmark[4]
    pinky = landmarks.landmark[20]

    tx, ty = int(thumb.x * W), int(thumb.y * H)
    px, py = int(pinky.x * W), int(pinky.y * H)

    dist = math.dist((tx, ty), (px, py))
    return tx, ty, px, py, dist

def detect_table_region(frame, prev_rect=None, area_thresh_ratio=0.25):
    """偵測桌面：畫面下半部最大矩形 + 閥值篩選。"""
    h, w, _ = frame.shape
    roi = frame[h // 2: h]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), 1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    best = None
    max_area = 0
    for c in contours:
        x, y, w_box, h_box = cv2.boundingRect(c)
        y += h // 2
        area = w_box * h_box

        # 更新最大面積
        if area > max_area:
            best = (x, y, w_box, h_box)
            max_area = area

    # 若無符合條件的 -> None
    if best is None:
        return None

    # 判斷是否與上一個桌面框接近（避免跳動）
    if prev_rect is not None:
        px, py, pw, ph = prev_rect
        bx, by, bw, bh = best

        # 桌面框差異不能太大
        if abs(px - bx) > w * 0.1:   # X 不能跳太多
            return None
        if abs(py - by) > h * 0.1:   # Y 不能跳太多
            return None

    return best