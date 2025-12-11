# utils/keyboard.py

import cv2
import math
from .display_text import draw_center_text

NOTE_MAP = {
    'C3': 48, 'D3': 50, 'E3': 52, 'F3': 53, 'G3': 55, 'A3': 57, 'B3': 59,
    'C4': 60, 'D4': 62, 'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72
}
NUM_KEYS = len(NOTE_MAP)
NUM_TO_NOTE = {v: k for k, v in NOTE_MAP.items()}

class Keyboard:
    def __init__(self, note_map):
        self.note_map = note_map
        self.num_keys = len(note_map)

        # 各個音
        self.notes_order = list(note_map.keys())

        # 每個 key 的範圍
        self.key_boxes = [] 

        # 琴鍵顏色
        self.white_color = (255, 255, 255)
        self.pressed_color = (180, 180, 180)
        self.practice_color =  (0, 255, 255)

        # 鍵盤設定
        self.key_height = 80  
        self.key_width = 80   

        self.key_radius = 28
        self.hit_threshold = 45

    def build_keyboard(self, table_rect):
        """
        依照桌面的 x, w 動態生成 15 顆圓形鍵盤位置
        """
        x, y, w, h = table_rect
        key_y = y - 25   # 琴鍵列（桌面正上方）
        step = w / len(self.notes_order)

        self.key_centers = []
        for i, note in enumerate(self.notes_order):
            cx = int(x + (i + 0.5) * step)
            self.key_centers.append((cx, key_y, note))

    def check_pressed(self, finger_positions):
        states = [0] * self.num_keys
        for fp in finger_positions:
            fx, fy = fp[0], fp[1]

            for i, (kx, ky, note) in enumerate(self.key_centers):
                if math.dist((fx, fy), (kx, ky)) < self.hit_threshold:
                    states[i] = 1
        pressed_notes = [self.notes_order[i] for i, s in enumerate(states) if s == 1]
        return pressed_notes

    def draw(self, frame, pressed_notes, next_note=None):
        """
        在桌面上方畫 15 顆圓形琴鍵（取代方形鋼琴鍵）
        """
        radius = self.key_radius

        for (cx, cy, note) in self.key_centers:

            if next_note == note and note not in pressed_notes:
                cv2.circle(frame, (cx, cy), radius+4, self.practice_color, -1)
                continue

            # 按下 → 實心，否則空心
            if note in pressed_notes:
                cv2.circle(frame, (cx, cy), radius, (0, 255, 0), -1)
            else:
                cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)

            # 標示音名
            cv2.putText(frame, note, (cx - 15, cy + 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
    def build_keyboard(self, frame_w, table_y, center_x, key_width):
        """
        根據桌面水平線 + 中心點 + 鍵寬動態生成圓形鍵盤位置
        frame_w  : 相機畫面寬度
        table_y  : 桌面 y 像素位置
        center_x : 食指所在的水平基準位置
        key_width: 推估的鍵間距（由手掌寬度決定）
        """

        num_keys = len(self.notes_order)

        # 以食指位置為中心，左右展開 15 顆鍵
        half = num_keys // 2

        self.key_centers = []

        for i, note in enumerate(self.notes_order):
            # ex: i = 0 → offset = -7
            offset = i - half
            cx = int(center_x + offset * key_width)
            cy = int(table_y - 35)

            self.key_centers.append((cx, cy, note))