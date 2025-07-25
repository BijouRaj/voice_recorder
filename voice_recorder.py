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
        #self.duration = 5
        self.channels = 2
        self.recording = []
        self.is_recording = False 
        self.stream = None 
        
        self.label = tk.Label(master, text="Click 'Start' to start recording.")
        self.label.pack(pady=10)
        
        self.start_button = tk.Button(master, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(master, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.save_button = tk.Button(master, text="Save Recording", command = self.save_recording, state=tk.DISABLED)
        self.save_button.pack(pady=5)
        
        self.play_button = tk.Button(master, text="Play Recording", command=self.play_recording, state=tk.DISABLED)
        self.play_button.pack(pady=5)
        
    def start_recording(self):
        self.label.config(text="Recording... Press 'Stop' to finish.")
        self.is_recording = True
        self.recording = []
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recording.append(indata.copy())
        
        self.stream = sd.InputStream(samplerate=self.freq, channels=self.channels, callback=callback)
        self.stream.start()
        
    def stop_recording(self):
        self.is_recording = False 
        self.stream.stop()
        self.stream.close()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.label.config(text="Recording stopped.")
        
        self.recording = np.concatenate(self.recording)
        
    def save_recording(self):
        try:
            if self.recording is not None:
                # Convert float32 to int16
                recording_int16 = np.int16(self.recording * 32767)
                
                write("manual_recording_scipy.wav", self.freq, recording_int16)
                wv.write("manual_recording_wavio.wav", self.recording, self.freq, sampwidth=2)
                messagebox.showinfo("Success", "Recording saved successfully.")
            else:
                messagebox.showwarning("Warning", "No recording to save.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def play_recording(self):
        if self.recording is not None and len(self.recording) > 0:
            sd.play(self.recording, self.freq)
        else:
            messagebox.showwarning("Warning", "No recording to play.")

# Create GUI window
root = tk.Tk()
app = VoiceRecorder(root)
root.mainloop()
