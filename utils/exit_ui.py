import cv2
import time

class ExitUI:
    def __init__(self):
        self.restart_btn = None
        self.exit_btn = None

        self.btn_w = 200
        self.btn_h = 70

        self.visible = False
        self.trigger_time = None  # 兩手離開鍵盤後開始計時

        self.default_color = (255, 255, 255)
        self.hover_color = (255, 200, 200)

    # 關閉系統的方式：雙手離開畫面3秒鐘以上，則會跳出退出或重新開始的選擇，若為record模式，則可以下載
    def update(self, left_up, right_up):
        if self.visible:
            return

        if left_up and right_up:
            if self.trigger_time is None:
                self.trigger_time = time.time()
            else:
                if time.time() - self.trigger_time >= 3.0:
                    self.visible = True
        else:
            self.trigger_time = None


    # restart / exit button
    def build(self, frame_w, frame_h):
        cx = frame_w // 2
        cy = frame_h // 2

        gap = 300  

        rx2 = cx - gap // 2
        rx1 = rx2 - self.btn_w
        ry1 = cy - self.btn_h // 2
        ry2 = cy + self.btn_h // 2

        ex1 = cx + gap // 2
        ex2 = ex1 + self.btn_w
        ey1 = ry1
        ey2 = ry2

        self.restart_btn = (rx1, ry1, rx2, ry2, "restart")
        self.exit_btn = (ex1, ey1, ex2, ey2, "exit")


    def check_pressed(self, fingers):
        if not self.visible:
            return None

        for (x, y, z) in fingers:
            for btn in [self.restart_btn, self.exit_btn]:
                (x1, y1, x2, y2, mode) = btn
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return mode
        return None

    def draw(self, frame, hover=None):
        if not self.visible:
            return

        for btn in [self.restart_btn, self.exit_btn]:
            (x1, y1, x2, y2, mode) = btn

            if hover == mode:
                color = self.hover_color
            else:
                color = self.default_color

            cv2.rectangle(frame, (x1, y1), (x2, y2),
                          (0, 0, 0), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2),
                          color, -1)

            text = "Restart" if mode == "restart" else "Exit"
            cv2.putText(frame, text,
                        (x1 + 25, y1 + 45),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 0, 0), 3)
