import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


def extract_audio(video_path, output_path):
    try:
        from moviepy import VideoFileClip
    except ImportError:
        from moviepy.editor import VideoFileClip

    video = VideoFileClip(video_path)
    try:
        if video.audio is None:
            raise ValueError("The selected video does not contain an audio track.")
        video.audio.write_audiofile(output_path)
    finally:
        video.close()


class AudioExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Extractor")
        self.root.geometry("680x310")
        self.root.minsize(600, 290)

        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="Choose a video to get started.")

        content = ttk.Frame(root, padding=(28, 24))
        content.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        ttk.Label(
            content, text="Extract audio from a video", font=("Segoe UI", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(
            content, text="Choose a video and save its soundtrack as an MP3 file."
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 18))
        ttk.Separator(content).grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 12))

        ttk.Label(content, text="Video file").grid(
            row=3, column=0, sticky="w", padx=(0, 12), pady=7
        )
        ttk.Entry(content, textvariable=self.video_path, state="readonly").grid(
            row=3, column=1, sticky="ew", pady=7
        )
        ttk.Button(content, text="Browse...", command=self.choose_video).grid(
            row=3, column=2, padx=(10, 0), pady=7
        )

        ttk.Label(content, text="Save MP3 to").grid(
            row=4, column=0, sticky="w", padx=(0, 12), pady=7
        )
        ttk.Entry(content, textvariable=self.output_path, state="readonly").grid(
            row=4, column=1, sticky="ew", pady=7
        )
        ttk.Button(content, text="Browse...", command=self.choose_output).grid(
            row=4, column=2, padx=(10, 0), pady=7
        )

        self.extract_button = ttk.Button(
            content, text="Extract audio", command=self.start_extraction
        )
        self.extract_button.grid(row=5, column=0, columnspan=3, pady=(18, 12))

        self.progress = ttk.Progressbar(content, mode="indeterminate")
        self.progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=4)
        ttk.Label(content, textvariable=self.status).grid(
            row=7, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

    def choose_video(self):
        path = filedialog.askopenfilename(
            title="Choose a video",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv *.webm *.mpeg *.mpg"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.video_path.set(path)
            self.output_path.set(str(Path(path).with_suffix(".mp3")))

    def choose_output(self):
        video_path = self.video_path.get()
        initial_file = f"{Path(video_path).stem}.mp3" if video_path else "audio_extracted.mp3"
        path = filedialog.asksaveasfilename(
            title="Save extracted audio",
            initialfile=initial_file,
            defaultextension=".mp3",
            filetypes=[("MP3 audio", "*.mp3")],
        )
        if path:
            self.output_path.set(path)

    def start_extraction(self):
        video_path = self.video_path.get()
        output_path = self.output_path.get()
        if not video_path:
            messagebox.showwarning("Choose a video", "Select a video file first.")
            return
        if not output_path:
            messagebox.showwarning("Choose an output", "Choose where to save the MP3 file.")
            return

        self.extract_button.configure(state="disabled")
        self.progress.start()
        self.status.set("Extracting audio...")
        threading.Thread(
            target=self._extract_in_background,
            args=(video_path, output_path),
            daemon=True,
        ).start()

    def _extract_in_background(self, video_path, output_path):
        try:
            extract_audio(video_path, output_path)
        except Exception as error:
            self.root.after(0, self._extraction_finished, output_path, error)
        else:
            self.root.after(0, self._extraction_finished, output_path, None)

    def _extraction_finished(self, output_path, error):
        self.progress.stop()
        self.extract_button.configure(state="normal")
        if error is not None:
            self.status.set("Audio extraction failed.")
            messagebox.showerror("Extraction failed", str(error))
            return

        self.status.set(f"Done: {output_path}")
        messagebox.showinfo("Extraction complete", f"Audio saved to:\n{output_path}")


if __name__ == "__main__":
    root = tk.Tk()
    AudioExtractorApp(root)
    root.mainloop()
