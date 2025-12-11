import cv2

class DownloadUI:
    def __init__(self):
        self.btn = None
        self.btn_w = 220
        self.btn_h = 80

        self.default_color = (255, 255, 255)
        self.hover_color = (200, 255, 200)

    def build(self, frame_w, frame_h):
        cx = frame_w // 2
        cy = int(frame_h * 0.75)

        x1 = cx - self.btn_w // 2
        y1 = cy - self.btn_h // 2
        x2 = cx + self.btn_w // 2
        y2 = cy + self.btn_h // 2

        self.btn = (x1, y1, x2, y2, "download")

    def check_pressed(self, fingers):
        if self.btn is None:
            return False

        (x1, y1, x2, y2, _) = self.btn

        for (x, y, z) in fingers:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True
        return False

    def draw(self, frame, hover=False):
        if self.btn is None:
            return

        (x1, y1, x2, y2, _) = self.btn

        color = self.hover_color if hover else self.default_color

        cv2.rectangle(frame, (x1, y1), (x2, y2),
                      (0, 0, 0), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2),
                      color, -1)

        cv2.putText(frame, "Download MIDI",
                    (x1 + 15, y1 + 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 0, 0), 3)
