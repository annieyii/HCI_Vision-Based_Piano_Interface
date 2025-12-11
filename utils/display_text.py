# utils/display_text.py
import cv2

def draw_center_text(frame, text, color=(0, 255, 255)):
    h, w, _ = frame.shape
    (tw, th), _ = cv2.getTextSize(text,
                                  cv2.FONT_HERSHEY_SIMPLEX,
                                  1.0, 2)
    x = int(w / 2 - tw / 2)
    y = int(h / 2 + th / 2)
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0, color, 2)
def draw_ui_messages(frame, table_locked, calibrated):
    h, w, _ = frame.shape
    baseY = h - 40

    if not table_locked:
        cv2.putText(frame, "Step1: Adjust camera until desk is boxed.", (10, baseY),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        cv2.putText(frame, "Press 'c' to LOCK desk.", (10, baseY+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
    elif not calibrated:
        cv2.putText(frame, "Step2: Place one hand above desk.", (10, baseY),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        cv2.putText(frame, "Press 'c' to CONFIRM hand width.", (10, baseY+25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
    else:
        cv2.putText(frame, "Virtual Piano Active — Tap keys with fingertips!",
                    (10, baseY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,255,200), 1)

    cv2.putText(frame, "q: quit | c: confirm | r: reset",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)