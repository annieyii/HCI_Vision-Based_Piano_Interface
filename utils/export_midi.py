# utils/export_midi.py
import mido
import time
import os
import subprocess
import pyautogui
from .keyboard import NOTE_MAP

def save_notes_to_midi(note_list, output_filename):
    if not note_list:
        print("沒有錄製到音符，跳過存檔。")
        return False

    print(f"正在轉換 {len(note_list)} 個音符...")
    ticks_per_beat = 480
    tempo = mido.bpm2tempo(120)
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    track.append(mido.Message('program_change', program=0, time=0))

    all_events = []
    note_duration = 0.4 # 假設每個音彈 0.4 秒
    
    for note_name, start_time in note_list:
        midi_pitch = NOTE_MAP.get(note_name)
        if midi_pitch is None: continue
        
        # Note On
        all_events.append((start_time, mido.Message('note_on', note=midi_pitch, velocity=90)))
        # Note Off
        all_events.append((start_time + note_duration, mido.Message('note_off', note=midi_pitch, velocity=0)))

    all_events.sort(key=lambda x: x[0])

    last_time = 0.0
    for abs_time, msg in all_events:
        delta = abs_time - last_time
        msg.time = int(mido.second2tick(delta, ticks_per_beat, tempo))
        track.append(msg)
        last_time = abs_time

    try:
        mid.save(output_filename)
        print(f"MIDI 檔案已儲存: {output_filename}")
        return True
    except Exception as e:
        print(f"儲存失敗: {e}")
        return False

def open_and_play_musescore(midi_filename):

    # Windows 預設路徑通常是這個：
    ms4_path = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
    
    # macOS 可能是這個：
    # ms4_path = "/Applications/MuseScore 4.app/Contents/MacOS/mscore"

    # 檢查路徑是否存在
    if not os.path.exists(ms4_path):
        print(f"找不到 MuseScore 4，請檢查路徑: {ms4_path}")
        return

    # 取得 MIDI 檔案的絕對路徑 (避免開錯檔案)
    abs_midi_path = os.path.abspath(midi_filename)

    print(f"正在開啟 MuseScore 4...")
    
    # 1. 開啟軟體
    try:
        subprocess.Popen([ms4_path, abs_midi_path])
    except Exception as e:
        print(f"無法開啟 MuseScore: {e}")
        return

    # 2. 等待軟體載入 (這很重要！)
    # MuseScore 4 啟動比較慢，視電腦效能可能需要 5~10 秒
    print("等待軟體載入中...")
    time.sleep(8) 

    # 3. 模擬按下空白鍵 (播放)
    # 為了保險，先點一下滑鼠左鍵確保視窗有被選取 (Focus)
    # 這裡抓螢幕中心點點一下 (MuseScore 通常會開在中間)
    screen_w, screen_h = pyautogui.size()
    pyautogui.click(screen_w // 2, screen_h // 2)
    
    time.sleep(0.5)
    print("開始播放！")
    pyautogui.press('space')

def convert_midi_to_pdf(midi_filename, ms4_path):
    """
    使用 MuseScore 4 的命令列功能，在背景將 MIDI 轉為 PDF
    """
    # 1. 準備檔案路徑 (轉成絕對路徑以防萬一)
    abs_midi = os.path.abspath(midi_filename)
    # 將副檔名 .mid 換成 .pdf
    abs_pdf = abs_midi.replace(".mid", ".pdf")
    
    print(f"正在轉檔為 PDF: {abs_pdf} ...")

    # 2. 執行指令
    # 指令格式: MuseScore4.exe -o "輸出檔名.pdf" "輸入檔名.mid"
    cmd = [ms4_path, '-o', abs_pdf, abs_midi]
    
    try:
        # subprocess.run 會等待轉檔完成才繼續往下執行
        subprocess.run(cmd, check=True)
        print("PDF 轉檔成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PDF 轉檔失敗: {e}")
        return False
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        return False

def process_recording(midi_filename):
    """
    這是要在 Thread 裡面跑的完整流程
    """
    # ms4_path = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
    ms4_path = r"/Applications/MuseScore 4.app/Contents/MacOS/mscore"
    # 設定 MuseScore 路徑 (請務必確認您的路徑是否正確)
    if not os.path.exists(ms4_path):
        print("找不到 MuseScore 4，請檢查路徑。")
        return
    
    convert_midi_to_pdf(midi_filename, ms4_path)

    
    print("正在開啟 MuseScore 視窗進行播放...")
    abs_midi_path = os.path.abspath(midi_filename)
    
    try:
        subprocess.Popen([ms4_path, abs_midi_path])
    except Exception as e:
        print(f"無法開啟軟體: {e}")
        return
    
    time.sleep(8) 
    
    screen_w, screen_h = pyautogui.size()
    pyautogui.click(screen_w // 2, screen_h // 2)
    time.sleep(0.5)
    
    # 按下空白鍵播放
    pyautogui.press('space')