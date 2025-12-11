# utils/practice_ui.py

import cv2
import os
import time
import mido
from .keyboard import NOTE_MAP, NUM_TO_NOTE

class PracticeUI:
    """
    Overlay style selection menu rendered inside main.py's frame.
    It displays MIDI files on the upper area of the screen.
    Hover fingertip on an item for >2 seconds to select.
    """
    def __init__(self, audio_dir="audio"):
        self.audio_dir = audio_dir
        self.files = [f for f in os.listdir(audio_dir) if f.endswith(".mid") or f.endswith(".midi")]

        # UI Layout
        self.menu_height = 250          # height of top overlay area
        self.item_height = 40           # each row height
        self.menu_bg = (230, 230, 230)  # light gray

        # State
        self.hover_start = None
        self.hovered_index = None
        self.selected_file = None

        self.midi_practice_audio = None
        self.practice_idx = 0

    def render(self, frame, fingertip):
        """
        Draw overlay menu on the frame & highlight hovered item.
        """
        h, w, _ = frame.shape

        # Create overlay background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (0, 0),
            (w, self.menu_height),
            self.menu_bg,
            -1
        )

        # Blend overlay with transparency
        alpha = 0.85
        frame[:self.menu_height] = cv2.addWeighted(
            overlay[:self.menu_height], alpha,
            frame[:self.menu_height], 1 - alpha, 0
        )

        # Draw title
        cv2.putText(
            frame, "Select MIDI File:",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2
        )

        # Draw file list
        for idx, file in enumerate(self.files):
            y = 70 + idx * self.item_height

            # Highlight if hovered
            if self.hovered_index == idx:
                cv2.rectangle(frame, (10, y - 25), (w - 10, y + 5), (180, 200, 255), -1)

            cv2.putText(
                frame,
                f"{idx+1}. {file}",
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 0),
                2
            )

        # Draw fingertip cursor
        if fingertip:
            fx, fy = fingertip
            cv2.circle(frame, (fx, fy), 8, (0, 255, 0), -1)

        return frame

    def update(self, fingertip):
        """
        Called every frame.
        Handles hover detection & selection logic.
        Returns the full file path when selected.
        """
        if fingertip is None:
            self.hovered_index = None
            self.hover_start = None
            return None

        fx, fy = fingertip

        # Only react if fingertip is inside menu area
        if fy > self.menu_height:
            self.hovered_index = None
            self.hover_start = None
            return None

        # Determine which item is hovered
        for idx in range(len(self.files)):
            y_top = 70 + idx * self.item_height - 25
            y_bottom = y_top + self.item_height

            if y_top <= fy <= y_bottom:
                # Set hovered index
                if self.hovered_index != idx:
                    self.hovered_index = idx
                    self.hover_start = time.time()   # reset hover timer
                else:
                    # Check if hovered for > 2 seconds
                    if time.time() - self.hover_start > 2:
                        self.selected_file = self.files[idx]
                        return os.path.join(self.audio_dir, self.selected_file)
                break
        else:
            self.hovered_index = None
            self.hover_start = None

        return None

    def is_active(self):
        return self.selected_file is None
    
    def midi_to_notes(self, path):
        """讀取 MIDI 並回傳 note sequence，例如 ["C4","C4","G4",...]"""
        mid = mido.MidiFile(path)
        notes = []

        for track in mid.tracks:
            for msg in track:
                if msg.type == "note_on" and msg.velocity > 0:
                    midi_num = msg.note
                    if midi_num in NUM_TO_NOTE:
                        notes.append(NUM_TO_NOTE[midi_num])  
                    else:
                        print(f"[Warning] Unknown MIDI note: {midi_num}")

        return notes