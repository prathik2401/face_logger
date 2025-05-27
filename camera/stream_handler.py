from django.http import StreamingHttpResponse
from .frame_provider import get_current_frame
import cv2
from face_recognition.recognizer import RecognizerPipeline
recognizer = RecognizerPipeline(matcher_threshold=0.4)

def stream_generator():
    while True:
        ret, frame = get_current_frame()
        if not ret:
            continue

        recognizer.process_frame(frame)
        
        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        
def live_feed_view(request):
    return StreamingHttpResponse(stream_generator(), content_type='multipart/x-mixed-replace; boundary=frame')
