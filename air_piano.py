# air_piano.py
import cv2
from utils.hand_tracker import HandTracker
from utils.mode_selector import ModeSelector
from utils.download_ui import DownloadUI
from utils.exit_ui import ExitUI
from utils.hand_processing import extract_finger_pixels
from utils.display_text import draw_center_text
from utils.keyboard import NOTE_MAP, Keyboard
from utils.record import MidiRecorder
from utils.soundplayer import SoundPlayer
from utils.practice_ui import PracticeUI

class AirPiano:
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        self.hand_tracker = HandTracker()
        self.keyboard = Keyboard(NOTE_MAP)
        self.mode_selector = ModeSelector()
        self.download_ui = DownloadUI()
        self.exit_ui = ExitUI()
        self.sound_player = SoundPlayer()
        self.midi_recorder = MidiRecorder()
        self.practice_ui = PracticeUI()

        self.mode = None  # 模式可選擇"record" or "practice"
        self.show_mode_text = False

        self.frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.table_ready = False
        self.keyboard_ready = False
        self.center_x = None
        self.key_width = None

        self.practice_idx = 0
        self.practice_notes = []

    def run(self):
        print("Please place your hand on the table for at least 1 second to calibrate.")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
                        
            left_hand, right_hand, left_z, right_z, handed_list = \
                self.hand_tracker.detect(frame)

            n_hands = 0
            if left_hand is not None:
                n_hands += 1
            if right_hand is not None:
                n_hands += 1

            # 1. 桌面校正
            if not self.hand_tracker.table_locked:
                self.hand_tracker.update_table_calibration(left_hand, right_hand, self.frame_h)
                draw_center_text(frame, "Please keep fingertip touching table for calibration.")

                cv2.imshow("AirPiano", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                continue
            
            if self.hand_tracker.table_y_pixel is not None:
                y = self.hand_tracker.table_y_pixel
                x = getattr(self.hand_tracker, "table_x_pixel", None)

                # 畫桌面水平線
                cv2.line(frame, (0, y), (self.frame_w, y), (0, 255, 0), 2)

                # 若有校正的 x，就畫圓心
                if x is not None:
                    cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)

            # 2. 手部校正
            if self.hand_tracker.table_locked and not self.keyboard_ready:
                draw_center_text(frame, "Step 2: Show your hand to calibrate key width.")

                dom = self.hand_tracker.get_dominant(left_hand, right_hand)

                if dom is None:
                    # 沒偵測到手，等手出現
                    cv2.imshow("AirPiano", frame)
                    if cv2.waitKey(1) & 0xFF == 27: break
                    continue
                
                hand = left_hand if dom == "Left" else right_hand

                palm_width = abs(hand[4][0] - hand[20][0]) * self.frame_w
                self.key_width = int(palm_width / 5) # 每個鍵的寬度

                finger_x = None
                if hand is not None: finger_x = int(hand[8][0] * self.frame_w) 

                self.keyboard.build_keyboard(self.frame_w, self.hand_tracker.table_y_pixel, finger_x, self.key_width)
                self.mode_selector.build_buttons(self.frame_w)

                self.keyboard_ready = True
                continue

            # 3. ModeSelector 選擇模式
            if self.mode is None:
                fingers = extract_finger_pixels(left_hand, right_hand, self.frame_w, self.frame_h)
                hover = self.mode_selector.check_pressed(fingers)

                if hover is not None:
                    self.mode = hover
                    self.show_mode_text = True

                    if self.mode == "record":
                        self.midi_recorder.start()
                    elif self.mode == "practice":
                        selected = None
                        while selected is None:
                            ret, frame = self.cap.read()
                            if not ret: break

                            frame = cv2.flip(frame, 1)
                            left_hand, right_hand, left_z, right_z, handed_list = self.hand_tracker.detect(frame)

                            # 取得手指座標
                            fingers = extract_finger_pixels(left_hand, right_hand,
                                                            self.frame_w, self.frame_h)
                            # 只需要右手的食指
                            fingertip = None
                            if right_hand is not None:  # 偵測到右手
                                x_norm, y_norm, _ = right_hand[8]   # 食指 (ID=8)
                                fx = int(x_norm * self.frame_w)
                                fy = int(y_norm * self.frame_h)
                                fingertip = (fx, fy)

                            # 顯示 UI
                            frame = self.practice_ui.render(frame, fingertip)
                            selected = self.practice_ui.update(fingertip)
                            cv2.imshow("AirPiano", frame)
                            if cv2.waitKey(1) & 0xFF == 27:
                                break

                        # 使用者已選好曲目
                        self.practice_ui.midi_practice_audio = selected
                        self.practice_ui.selected_file = selected

                        # 讀取 MIDI → 轉成鍵盤可用的 note sequence
                        self.practice_notes = self.practice_ui.midi_to_notes(selected)
                        print("Loaded practice notes:", self.practice_notes)
                        self.practice_idx = 0

                self.mode_selector.draw(frame, hover)

                draw_center_text(frame, "Please select a mode: Record or Practice.")
                cv2.imshow("AirPiano", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    break
                continue

            # 顯示當前選擇模式 1 秒
            if self.show_mode_text:
                msg = "RECORD MODE" if self.mode == "record" else "PRACTICE MODE"
                draw_center_text(frame, msg)
                cv2.imshow("AirPiano", frame)
                cv2.waitKey(1000)
                self.show_mode_text = False

            # 4. 取得手指位置（10 指）
            fingers = extract_finger_pixels(left_hand, right_hand, self.frame_w, self.frame_h)

            # 5. 檢查哪些鍵被按下
            pressed_notes = self.keyboard.check_pressed(fingers)

            # 6.音效播放（多音）
            self.sound_player.play_notes(pressed_notes)

            # 停止已放開的鍵
            all_notes = list(NOTE_MAP.keys())
            released_notes = [n for n in all_notes if n not in pressed_notes]
            self.sound_player.stop_notes(released_notes)

            # 7.若是錄音模式 → 更新 MIDI
            if self.mode == "record":
                self.midi_recorder.update(pressed_notes)

            # 8. 離開 Exit UI
            left_up = left_hand is None
            right_up = right_hand is None
            self.exit_ui.update(left_up, right_up)

            # 若 Exit UI 開啟 → 檢查按鈕
            if self.exit_ui.visible:
                self.exit_ui.build(self.frame_w, self.frame_h)

                midi_hover = False
                # 只有在 record 模式才顯示 Download MIDI
                if self.mode == "record":
                    self.download_ui.build(self.frame_w, self.frame_h)
                    midi_hover = self.download_ui.check_pressed(fingers)

                    if midi_hover:
                        midi_file = self.midi_recorder.stop_and_save()
                        draw_center_text(frame, f"Saved: {midi_file}")
                        cv2.imshow("AirPiano", frame)
                        cv2.waitKey(500)  # 短暫顯示一下提示

                # 檢查 Exit / Restart
                selected = self.exit_ui.check_pressed(fingers)

                if selected == "exit":
                    print("程式結束")
                    break

                elif selected == "restart":
                    print("Restart requested")

                    # 重置模式狀態
                    self.mode = None
                    self.show_mode_text = False

                    # 重置鍵盤 / 校正狀態
                    self.keyboard_ready = False
                    self.center_x = None
                    self.key_width = None

                    # 重置 hand_tracker 的桌面校正狀態
                    self.hand_tracker.table_locked = False
                    self.hand_tracker.table_lock_time = None

                    self.exit_ui.visible = False
                    self.exit_ui.trigger_time = None

                    # 5. 重建一個新的 MIDI recorder
                    self.midi_recorder = MidiRecorder()
                    continue


                # 繪製 Exit UI
                self.exit_ui.draw(frame)

                # 若是 record 模式，再畫 Download 按鈕
                if self.mode == "record":
                    self.download_ui.draw(frame, midi_hover)

                cv2.imshow("AirPiano", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                continue

            # 練習模式 → 只畫鍵盤
            if self.mode == "practice":
                next_note = self.practice_notes[self.practice_idx]
                # self.keyboard.highlight_note(next_note)

                # 如果使用者按對
                if next_note in pressed_notes:
                    self.sound_player.play_notes([next_note])
                    self.practice_idx += 1

                    # 如果彈完了，show success
                    if self.practice_idx >= len(self.practice_notes):
                        draw_center_text(frame, "Song Completed!")
                        cv2.imshow("AirPiano", frame)
                        cv2.waitKey(1500)
                        self.mode = None
                        continue

                # self.keyboard.draw(frame, pressed_notes)
                self.keyboard.draw(frame, pressed_notes, next_note)

            # 錄音模式 → 錄完可下載 MIDI
            if self.mode == "record":
                self.keyboard.draw(frame, pressed_notes)

            # 畫面更新
            cv2.imshow("AirPiano", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = AirPiano(cam_index=0)
    app.run()
