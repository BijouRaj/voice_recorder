# import libraries

# library providing functions to play and record NumPy arrays containing audio signals
import sounddevice as sd 

# saves recorded audio in file format
from scipy.io.wavfile import write
import wavio as wv 

# gui libraries
import tkinter as tk 
from tkinter import messagebox 
import threading 
import numpy as np 

# defined class for voice recorder
class VoiceRecorder:
    def __init__(self, master):
        self.master = master 
        master.title("Voice Recorder")
        
        self.freq = 44100
        self.duration = 5
        self.channels = 2
        self.recording = None 
        
        self.label = tk.Label(master, text="Press 'Record' to start recording.")
        self.label.pack(pady=10)
        
        self.record_button = tk.Button(master, text="Record", command=self.start_recording)
        self.record_button.pack(pady=5)
        
        self.save_button = tk.Button(master, text="Save Recording", command = self.save_recording, state=tk.DISABLED)
        self.save_button.pack(pady=5)
        
        self.play_button = tk.Button(master, text="Play Recording", command=self.play_recording, state=tk.DISABLED)
        self.play_button.pack(pady=5)
        
    def start_recording(self):
        self.label.config(text="Recording...")
        self.record_button.config(state=tk.DISABLED)
        threading.Thread(target=self.record_audio).start()
        
    def record_audio(self):
        try: 
            self.recording = sd.rec(int(self.duration * self.freq), samplerate=self.freq, channels=self.channels)
            sd.wait()
            self.label.config(text="Recording finished.")
            self.save_button.config(state=tk.NORMAL)
            self.play_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
        self.record_button.config(state=tk.NORMAL)
        
    def save_recording(self):
        try:
            if self.recording is not None:
                # Convert float32 to int16
                recording_int16 = np.int16(self.recording * 32767)
                
                write("recording_gui_scipy.wav", self.freq, recording_int16)
                wv.write("recording_gui_wavio.wav", self.recording, self.freq, sampwidth=2)
                messagebox.showinfo("Success", "Recording saved successfully.")
            else:
                messagebox.showwarning("Warning", "No recording to save.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def play_recording(self):
        if self.recording is not None:
            sd.play(self.recording, self.freq)
        else:
            messagebox.showwarning("Warning", "No recording to play.")

# Create GUI window
root = tk.Tk()
app = VoiceRecorder(root)
root.mainloop()
