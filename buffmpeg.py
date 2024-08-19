"""
This is a simple video cutter GUI application that uses ffmpeg to cut videos.
Mainly, this is to get file sizes down to be sent over Discord.
The user can specify the input video file, output directory, start time, and end time.
 
To install this script's dependencies, run:
    pip install tk

Further downloads are needed for ffmpeg (video cutting) and ffprobe (obtaining video duration)
these are available from https://ffmpeg.org/download.html
Download these if needed, and place them in a 'tools' directory in the same directory as this script.

Your directory should look like this:
 .
 ├── buffmpeg.py
 ├── tools
 │   ├── ffmpeg.exe
 │   └── ffprobe.exe

"""

import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
from datetime import datetime
import zipfile

class VideoCutterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Cutter")
        self.geometry("600x600")

        # Determine the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the working directory to the script's directory
        os.chdir(script_dir)

        # Input Directory UI
        tk.Label(self, text="Input Directory:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.input_dir = tk.Entry(self, width=50)
        self.input_dir.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=10, pady=10)

        # Output Directory UI
        tk.Label(self, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.output_dir = tk.Entry(self, width=50)
        self.output_dir.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=10, pady=10)

        # FFMPEG Directory UI
        tk.Label(self, text="FFMPEG Location:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.ffmpeg_dir = tk.Entry(self, width=50)
        self.ffmpeg_dir.grid(row=2, column=1, padx=10, pady=10)
        # display text in the box to tell user this isnt needed
        self.ffmpeg_dir.insert(0, "Not needed if ffmpeg is in the tools directory")

        tk.Button(self, text="Browse...", command=self.browse_ffmpeg).grid(row=2, column=2, padx=10, pady=10)

        # Output File Name UI
        tk.Label(self, text="Output File Name:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.output_name = tk.Entry(self, width=50)
        ## have the user input box say something
        self.output_name.grid(row=3, column=1, padx=10, pady=10)

        # Quality Options UI
        tk.Label(self, text="Quality:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.quality_var = tk.StringVar(value="Preserve Original")
        tk.OptionMenu(self, self.quality_var, "Preserve Original", "High Quality", "Medium Quality", "Low Quality").grid(row=4, column=1, padx=10, pady=10, sticky='w')

        # Start Time UI
        tk.Label(self, text="Start Time:").grid(row=5, column=0, padx=10, pady=10, sticky='e')
        self.start_time_h = tk.Entry(self, width=2)
        self.start_time_h.grid(row=5, column=1, sticky='w')
        tk.Label(self, text="h").grid(row=5, column=1, padx=(25, 0), sticky='w')
        self.start_time_m = tk.Entry(self, width=2)
        self.start_time_m.grid(row=5, column=1, padx=(50, 0), sticky='w')
        tk.Label(self, text="m").grid(row=5, column=1, padx=(75, 0), sticky='w')
        self.start_time_s = tk.Entry(self, width=2)
        self.start_time_s.grid(row=5, column=1, padx=(100, 0), sticky='w')
        tk.Label(self, text="s").grid(row=5, column=1, padx=(125, 0), sticky='w')

        # End Time UI
        tk.Label(self, text="End Time:").grid(row=6, column=0, padx=10, pady=10, sticky='e')
        self.end_time_h = tk.Entry(self, width=2)
        self.end_time_h.grid(row=6, column=1, sticky='w')
        tk.Label(self, text="h").grid(row=6, column=1, padx=(25, 0), sticky='w')
        self.end_time_m = tk.Entry(self, width=2)
        self.end_time_m.grid(row=6, column=1, padx=(50, 0), sticky='w')
        tk.Label(self, text="m").grid(row=6, column=1, padx=(75, 0), sticky='w')
        self.end_time_s = tk.Entry(self, width=2)
        self.end_time_s.grid(row=6, column=1, padx=(100, 0), sticky='w')
        tk.Label(self, text="s").grid(row=6, column=1, padx=(125, 0), sticky='w')

        # Zip Option
        self.zip_var = tk.IntVar()
        self.zip_check = tk.Checkbutton(self, text="Zip the output file", variable=self.zip_var)
        self.zip_check.grid(row=5, column=2, pady=10)

        # Crush Entire Video Option
        self.crush_entire_var = tk.IntVar()
        self.crush_entire_check = tk.Checkbutton(self, text="Crush Entire Video", variable=self.crush_entire_var, command=self.set_entire_video_duration)
        self.crush_entire_check.grid(row=6, column=2, pady=10)

        # Cut Button
        tk.Button(self, text="Cut It!", command=self.cut_video).grid(row=4, column=2, pady=20)

        # Log Output
        self.log_output = tk.Text(self, width=70, height=10)
        self.log_output.grid(row=7, column=0, columnspan=3, padx=10, pady=10)
        tk.Button(self, text="Clear Output", command=self.clear_log).grid(row=9, column=1, pady=10)

        # Default ffmpeg path using a relative path turned into an absolute path
        self.default_ffmpeg_path = os.path.join(script_dir, 'tools', 'ffmpeg.exe')

    # Open file dialogues to get the input, output, and ffmpeg directories
    def browse_input(self):
        filename = filedialog.askopenfilename()
        self.input_dir.insert(0, filename)
        self.show_video_duration()

    def browse_output(self):
        directory = filedialog.askdirectory()
        self.output_dir.insert(0, directory)

    def browse_ffmpeg(self):
        ffmpeg_path = filedialog.askopenfilename(filetypes=[("FFmpeg Executable", "ffmpeg.exe")])
        self.ffmpeg_dir.insert(0, ffmpeg_path)

    def clear_log(self):
        self.log_output.delete(1.0, tk.END)

    # Show the video duration in the log output
    def show_video_duration(self):
        input_file = self.input_dir.get()
        if not input_file:
            return
        try:
            duration = self.get_video_duration(input_file)
            self.log(f"Video Duration: {duration:.2f} seconds")
            self.log(f"Video Duration: {duration / 60:.2f} minutes")
        except Exception as e:
            self.log(f"[Error:] Could not retrieve video duration: {str(e)}")

    def get_video_duration(self, filename):
        # Assuming ffprobe is in the same directory as ffmpeg
        ffprobe_path = os.path.join(os.path.dirname(self.ffmpeg_dir.get() or self.default_ffmpeg_path), "ffprobe.exe")

        ffprobe_cmd = [
            ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filename
        ]
        result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe error: {result.stderr.strip()}")
        return float(result.stdout.strip())

    def set_entire_video_duration(self):
        if self.crush_entire_var.get() == 1:
            try:
                duration = self.get_video_duration(self.input_dir.get())
                self.start_time_h.delete(0, tk.END)
                self.start_time_m.delete(0, tk.END)
                self.start_time_s.delete(0, tk.END)
                self.start_time_h.insert(0, "0")
                self.start_time_m.insert(0, "0")
                self.start_time_s.insert(0, "0")

                self.end_time_h.delete(0, tk.END)
                self.end_time_m.delete(0, tk.END)
                self.end_time_s.delete(0, tk.END)

                end_hours = int(duration // 3600)
                end_minutes = int((duration % 3600) // 60)
                end_seconds = int(duration % 60)

                self.end_time_h.insert(0, str(end_hours))
                self.end_time_m.insert(0, str(end_minutes))
                self.end_time_s.insert(0, str(end_seconds))

                self.log(f"[Info:] Set to crush entire video: {end_hours}h {end_minutes}m {end_seconds}s")
            except Exception as e:
                self.log(f"[Error:] Could not set video duration: {str(e)}")
        else:
            self.log("[Info:] Crush entire video option deselected.")

    def cut_video(self):
        input_file = self.input_dir.get()
        output_dir = self.output_dir.get()
        ffmpeg_path = self.ffmpeg_dir.get() or self.default_ffmpeg_path

        # Handle empty hour input by setting default value to 0
        start_time_h = self.start_time_h.get() or "0"
        start_time_m = self.start_time_m.get() or "0"
        start_time_s = self.start_time_s.get() or "0"
        end_time_h = self.end_time_h.get() or "0"
        end_time_m = self.end_time_m.get() or "0"
        end_time_s = self.end_time_s.get() or "0"

        start_time = f"{start_time_h}:{start_time_m}:{start_time_s}"
        end_time = f"{end_time_h}:{end_time_m}:{end_time_s}"

        # Generate the output name based on the user input or current date and time
        output_name = self.output_name.get() or datetime.now().strftime('crushed-video-%m-%d-%H-%M-%S')
        output_file = os.path.join(output_dir, f"{output_name}.mp4")

        # Error Handling of User Input
        # Validate user input
        if not input_file or not output_dir:
            self.log("[Error:] Please fill in all fields.")
            return

        # Ensure start time is earlier than end time
        if start_time >= end_time:
            self.log("[Error:] Start time must be earlier than end time.")
            return

        # Check if ffmpeg path is valid
        if not os.path.isfile(ffmpeg_path):
            self.log("[Error:] The specified path to ffmpeg.exe cannot be found.")
            return

        # Check if the end time exceeds the video duration
        try:
            duration = self.get_video_duration(input_file)
            total_end_time = int(end_time_h) * 3600 + int(end_time_m) * 60 + int(end_time_s)
            if total_end_time > duration:
                self.log("[Error:] The end time exceeds the video duration.")
                return
        except Exception as e:
            self.log(f"[Error:] Could not validate video duration: {str(e)}")
            return

        # Choose the compression level based on user selection
        quality = self.quality_var.get()
        if quality == "Preserve Original":
            codec_options = ['-c', 'copy']
        elif quality == "High Quality":
            codec_options = ['-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-c:a', 'aac', '-b:a', '192k']
        elif quality == "Medium Quality":
            codec_options = ['-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'aac', '-b:a', '128k']
        elif quality == "Low Quality":
            codec_options = ['-c:v', 'libx264', '-crf', '28', '-preset', 'fast', '-c:a', 'aac', '-b:a', '96k']
        else:
            self.log(f"[Error:] Unknown quality setting: {quality}")
            return

        # Process video using direct ffmpeg command with the selected codec options
        try:
            command = [
                ffmpeg_path,  # Use user-defined or default path to ffmpeg
                '-i', input_file,
                '-ss', start_time,
                '-to', end_time,
            ] + codec_options + [output_file]
            subprocess.run(command, check=True)
            self.log(f"[Success:] Video has been cut to {output_file}. File size is {os.path.getsize(output_file) / (1024 * 1024):.2f} MB.")

            # Check file size and warn if > 25MB
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            if file_size > 25:
                self.log(f"[Warning:] File size is {file_size:.2f} MB, which is larger than 25 MB.")
                self.log("[Info:] Consider compressing or zipping the file.")

            # Zip the output file if the user selected the option
            if self.zip_var.get() == 1:
                zip_file_path = os.path.join(output_dir, f"{output_name}.zip")
                with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(output_file, os.path.basename(output_file))
                self.log(f"[Success:] Output file has been zipped as {zip_file_path}")

        except Exception as e:
            self.log(f"[Error:] {str(e)}")

    def log(self, message):
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.yview(tk.END)

if __name__ == "__main__":
    app = VideoCutterApp()
    app.mainloop()
