# utils/record.py
import os
from mido import Message, MidiFile, MidiTrack
import time
from .keyboard import NOTE_MAP
from .export_midi import save_notes_to_midi, process_recording

class MidiRecorder:
    def __init__(self):
        self.mid = MidiFile()
        self.track = MidiTrack()
        self.mid.tracks.append(self.track)

        self.active = False
        self.note_on_time = {}

        self.last_time = time.time()
        
    def start(self):
        self.active = True
        self.track = MidiTrack()
        self.mid.tracks = [self.track]
        self.last_time = time.time()
        self.note_on_time = {}
        print("MIDI recording started")

    def stop_and_save(self):
        if not self.active:
            return None

        self.active = False

        directory = "./records"
        os.makedirs(directory, exist_ok=True)

        # 預設使用timestamp命名
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(directory, f"recording_{ts}.mid")
        self.mid.save(filename)
        print(f"MIDI saved to {filename}")
        process_recording(filename)
        return filename

    def update(self, pressed_notes):
        if not self.active:
            return

        now = time.time()
        dt = now - self.last_time
        delta_ticks = int(dt * 480)

        for n in pressed_notes:
            if n not in self.note_on_time:
                midi_num = NOTE_MAP[n]
                self.track.append(Message("note_on", note=midi_num, velocity=90, time=delta_ticks))
                self.note_on_time[n] = now
                dt = 0  

        # 處理 note off（手已放開的）
        for n in list(self.note_on_time.keys()):
            if n not in pressed_notes:
                midi_num = NOTE_MAP[n]
                self.track.append(Message("note_off", note=midi_num, velocity=0, time=delta_ticks))
                del self.note_on_time[n]
                dt = 0

        self.last_time = now
    def toggle(self):
        """切換錄音狀態"""
        if not self.is_recording:
            # --- 開始錄音 ---
            self.is_recording = True
            self.start_time = time.time()
            self.recorded_notes = []
            print("[REC] 開始錄音...")
        else:
            # --- 停止並存檔 ---
            self.is_recording = False
            print("[REC] 停止錄音，正在存檔...")
            filename = f"record_{int(time.time())}.mid"
            save_notes_to_midi(self.recorded_notes, filename)

            # 呼叫轉檔
            success = save_notes_to_midi(self.recorded_notes, filename)
            
            # 如果成功，就開啟 MuseScore
            if success:
                # 這裡呼叫自動播放函式
                # 注意：這會暫停您的 python 視窗約 8 秒鐘等待 MuseScore 開啟
                process_recording(filename)
    def add_note(self, note_name):
        """
        讓外部程式呼叫此函式來加入音符
        """
        if self.is_recording:
            rel_time = time.time() - self.start_time
            self.recorded_notes.append((note_name, rel_time))
            print(f" >> 錄製: {note_name} ({rel_time:.2f}s)")