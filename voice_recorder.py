# import libraries

# library providing functions to play and record NumPy arrays containing audio signals
import sounddevice as sd 

# saves recorded audio in file format
from scipy.io.wavfile import write # saves using SciPy
import wavio as wv # alternate WAV writer, supports floating-point arrays

# gui libraries
import tkinter as tk # GUI toolkit
from tkinter import messagebox 
import threading # allows recording/playback timers without freezing UI
import numpy as np # stores and manipulates audio signals
import time # time, duh, measures durations and animations
import matplotlib.pyplot as plt # for plotting waveform
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # embeds waveforms into Tkinter GUI

# defined class for voice recorder
class VoiceRecorder:
    def __init__(self, master):
        # master is main Tkinter window
        self.master = master 
        master.title("Voice Recorder")
        
        # initializes state variables
        self.freq = 44100 # sample rate
        self.channels = 2 # stereo channels
        self.recording = [] # audio buffer
        self.is_recording = False 
        self.stream = None 
        self.start_time = None 
        self.timer_thread = None 
        self.canvas = None 
        
        # UI components, creates interface
        self.label = tk.Label(master, text="Click 'Start' to start recording.")
        self.label.pack(pady=10)
        
        # input field for filename
        self.filename_label = tk.Label(master, text="Filename (without .wav):")
        self.filename_label.pack()
        self.filename_entry = tk.Entry(master, width=30)
        self.filename_entry.insert(0, "my_recording")
        self.filename_entry.pack(pady=5)
        
        # buttons
        self.start_button = tk.Button(master, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(master, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.save_button = tk.Button(master, text="Save Recording", command = self.save_recording, state=tk.DISABLED)
        self.save_button.pack(pady=5)
        
        self.play_button = tk.Button(master, text="Play Recording", command=self.play_recording, state=tk.DISABLED)
        self.play_button.pack(pady=5)
        
        # frame to display waveform
        self.plot_frame = tk.Frame(master)
        self.plot_frame.pack(pady=10)
        
    # function for starting recording
    def start_recording(self):
        # UI
        self.label.config(text="Recording... 0s")
        self.is_recording = True
        # holds recording
        self.recording = []
        # for recording time, obviously
        self.start_time = time.time()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # continuously adds audio chunks into recording array
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recording.append(indata.copy())
        
        # records audio using sounddevice.InputStream
        self.stream = sd.InputStream(samplerate=self.freq, channels=self.channels, callback=callback)
        self.stream.start()
        
        # starts separate thread to update elapsed time each second
        self.timer_thread = threading.Thread(target = self.update_timer)
        self.timer_thread.start()
        
    # function to update timer
    def update_timer(self):
        while self.is_recording:
            # easy math to find elapsed time
            elapsed = int(time.time() - self.start_time)
            self.label.config(text=f"Recording... {elapsed}s")
            time.sleep(1)
        
    # function to stop recording
    def stop_recording(self):
        self.is_recording = False 
        # stops and closes stream
        self.stream.stop()
        self.stream.close()
        
        # update button states for GUI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.label.config(text="Recording stopped.")
        
        # concatenates recorded audio chunks into numpy array
        self.recording = np.concatenate(self.recording)
        
        # calls upon function to plot the waveform
        self.plot_waveform()
        
    # function to plot waveform
    def plot_waveform(self):
        # Remove existing waveform
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        # creates new figure and axes for waveform
        self.fig, self.ax = plt.subplots(figsize=(6, 2), dpi=100)
        ax = self.ax
        # plots mono audio directly
        if self.channels == 1:
            ax.plot(self.recording, color='blue')
        # plots stereo channels separately
        else:
            ax.plot(self.recording[:, 0], label="Left", color='blue')
            ax.plot(self.recording[:, 1], label="Right", color='red')
            ax.legend(loc='upper right')
            
        ax.set_title("Waveform Preview")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Amplitude")
        # plot entire waveform for recording
        ax.set_xlim(0, len(self.recording))
        ax.set_ylim(-1.0, 1.0)
        
        self.fig.tight_layout()
        
        # embeds plot into Tkinte rGUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        
    # function to save waveform
    def save_recording(self):
        try:
            if self.recording is not None:
                # Convert float32 to int16
                recording_int16 = np.int16(self.recording * 32767)
                
                # gets filename from entry field, otherwise names as my_recording
                filename = self.filename_entry.get().strip()
                if not filename:
                    filename = "my_recording"
                
                # saves using both scipy and wavio
                write(f"{filename}_scipy.wav", self.freq, recording_int16)
                wv.write(f"{filename}_wavio.wav", self.recording, self.freq, sampwidth=2)
                messagebox.showinfo("Success", "Recording saved successfully.")
            else:
                messagebox.showwarning("Warning", "No recording to save.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    # function to play recording
    def play_recording(self):
        if self.recording is not None and len(self.recording) > 0:
            self.play_button.config(state=tk.DISABLED)
            self.label.config(text="Playing...")
            
            # 
            duration = len(self.recording) / self.freq 
            total_samples = len(self.recording)
            scroll_window = self.freq * 2 
            
            if hasattr(self, 'cursor_line') and self.cursor_line:
                self.cursor_line.remove()
                self.cursor_line = None
                
            # adds vertical line to scroll along for progress
            self.cursor_line = self.ax.axvline(x=0, color='red')
            self.canvas.draw()
            
            # animation for the cursor
            def update_cursor():
                start_time = time.time()
                while True:
                    # track elapsed time, map to waveform
                    elapsed = time.time() - start_time 
                    sample_index = int(elapsed * self.freq)
                    
                    # if at end of sample, break
                    if sample_index >= total_samples:
                        break 
                        
                    self.cursor_line.set_xdata([sample_index])
                    
                    # scroll window with cursor
                    if sample_index > scroll_window:
                        self.ax.set_xlim(sample_index - scroll_window, sample_index + scroll_window)
                    else:
                        self.ax.set_xlim(0, scroll_window * 2)
                        
                    # redraws updated cursor
                    self.canvas.draw_idle()
                    time.sleep(0.02)
                    
                self.label.config(text="Playback finished.")
                self.play_button.config(state=tk.NORMAL)
                
            # playback audio and animate cursor in parallel, update cursor in background thread so playback and UI remain responsive
            threading.Thread(target=update_cursor).start()
            # actual audio playback using sounddevice
            sd.play(self.recording, self.freq)
        else:
            messagebox.showwarning("Warning", "No recording to play.")

# Create GUI window, launches GUI application
root = tk.Tk()
app = VoiceRecorder(root)
root.mainloop()
