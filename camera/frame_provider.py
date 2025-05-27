from .video_stream import VideoStream

video_stream = VideoStream(src=0)

def get_current_frame():
    return video_stream.get_frame()
