try:
	from moviepy import VideoFileClip  
except ImportError:
	from moviepy.editor import VideoFileClip  

video = VideoFileClip("Video1.mp4")
ext_aud = video.audio

ext_aud.write_audiofile("audio_extracted.mp3")