# utils/soundplayer.py
import pygame
import os
from .keyboard import NOTE_MAP

class SoundPlayer:
    def __init__(self, wav_folder="sounds_WAV"):
        pygame.mixer.init()
        self.sounds = {}
        for note, midi in NOTE_MAP.items():
            wav_path = os.path.join(wav_folder, f"{note}.wav")
            if os.path.exists(wav_path):
                self.sounds[note] = pygame.mixer.Sound(wav_path)
            else:
                print(f"Warning! Missing wav file: {wav_path}")

        self.active_channels = {}

    def play_notes(self, notes):
        for note in notes:
            if note not in self.sounds:
                continue

            if note not in self.active_channels:
                ch = self.sounds[note].play()
                self.active_channels[note] = ch

    def stop_notes(self, notes):
        for note in notes:
            if note in self.active_channels:
                ch = self.active_channels[note]
                if ch:
                    ch.stop()
                del self.active_channels[note]