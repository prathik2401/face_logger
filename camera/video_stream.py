import cv2
import threading

class VideoStream:
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        if not self.capture.isOpened():
            raise ValueError(f"Unable to open the video source {src}.")

        self.lock = threading.Lock()
        self.ret, self.frame = self.capture.read()
        self.running = True

        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            with self.lock:
                self.ret, self.frame = self.capture.read()

    def get_frame(self):
        with self.lock:
            return self.ret, self.frame.copy() if self.ret else  (False, None)

    def release(self):
        self.running = False
        self.capture.release()
