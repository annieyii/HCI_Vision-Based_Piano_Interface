import cv2

class ModeSelector:
    def __init__(self):
        self.record_btn = None
        self.practice_btn = None

        # 顏色設定
        self.record_color = (0, 0, 255)
        self.practice_color = (0, 255, 0)
        self.hover_color = (255, 255, 0)

    def build_buttons(self, frame_w, frame_h=480):
        btn_width = frame_w // 3
        btn_height = 60

        y_center = 80
        y1 = y_center - btn_height // 2
        y2 = y_center + btn_height // 2

        # Record 在左
        rx1 = frame_w // 4 - btn_width // 2
        rx2 = rx1 + btn_width

        # Practice 在右
        px1 = 3 * frame_w // 4 - btn_width // 2
        px2 = px1 + btn_width

        self.record_btn = (rx1, y1, rx2, y2)
        self.practice_btn = (px1, y1, px2, y2)

    def check_pressed(self, fingers):
        if self.record_btn is None or self.practice_btn is None:
            return None

        rx1, ry1, rx2, ry2 = self.record_btn
        px1, py1, px2, py2 = self.practice_btn

        for (fx, fy, fz) in fingers:
            if rx1 <= fx <= rx2 and ry1 <= fy <= ry2:
                return "record"
            if px1 <= fx <= px2 and py1 <= fy <= py2:
                return "practice"

        return None

    def draw(self, frame, hover=None):
        if self.record_btn is None or self.practice_btn is None:
            return

        rx1, ry1, rx2, ry2 = self.record_btn
        px1, py1, px2, py2 = self.practice_btn

        base_color = (255, 255, 255)      # 預設白色
        hover_color = (180, 180, 180)     # hover會變灰色
        outline = (0, 0, 0)               
        font_color = (0, 0, 0)           

        color = hover_color if hover == "record" else base_color
        cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), color, -1)
        cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), outline, 2)
        cv2.putText(frame, "RECORD",
                    (rx1 + 20, ry1 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, font_color, 2)

        color = hover_color if hover == "practice" else base_color
        cv2.rectangle(frame, (px1, py1), (px2, py2), color, -1)
        cv2.rectangle(frame, (px1, py1), (px2, py2), outline, 2)
        cv2.putText(frame, "PRACTICE",
                    (px1 + 20, py1 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, font_color, 2)

