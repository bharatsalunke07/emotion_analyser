import threading
import time
import cv2
import numpy as np
from deepface import DeepFace

# Settings
CAMERA_INDEX = 0
ANALYZE_EVERY_N_FRAMES = 6
FORCE_FLIP = 1
EMOJI_MAP = {
    'happy': '😄', 'sad': '😢', 'angry': '😠', 'surprise': '😲', 'neutral': '😐', 'fear': '😨', 'disgust': '🤢'
}
EMOTION_LIST = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

class DetectorThread:
    def __init__(self):
        self.cap = None
        self.thread = None
        self.running = False
        self.lock = threading.Lock()
        self.frame = None
        self.last_analysis = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.frame_count = 0

    def start(self):
        with self.lock:
            if self.running:
                return False
            self.cap = cv2.VideoCapture(CAMERA_INDEX)
            if not self.cap.isOpened():
                raise RuntimeError("Could not open webcam")
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            return True

    def stop(self):
        with self.lock:
            if not self.running:
                return False
            self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        return True

    def _run(self):
        while True:
            with self.lock:
                if not self.running:
                    break
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            if FORCE_FLIP is not None:
                frame = cv2.flip(frame, FORCE_FLIP)

            self.frame_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

            for (x, y, w, h) in faces:
                pad = int(0.1 * w)
                x1, y1 = max(0, x - pad), max(0, y - pad)
                x2, y2 = min(frame.shape[1], x + w + pad), min(frame.shape[0], y + h + pad)
                face_img = frame[y1:y2, x1:x2]
                if self.frame_count % ANALYZE_EVERY_N_FRAMES == 0:
                    try:
                        analysis = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
                        if isinstance(analysis, list):
                            analysis = analysis[0]
                        self.last_analysis = analysis
                    except Exception:
                        pass
                if self.last_analysis:
                    dominant = self.last_analysis.get('dominant_emotion', '')
                    score = 0
                    emotions = self.last_analysis.get('emotion', {})
                    if dominant in emotions:
                        score = emotions[dominant]
                    emoji = EMOJI_MAP.get(dominant, '')
                    label = f"{emoji} {dominant} ({score:.0f}%)"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            frame = self._draw_emotion_bar_graph(frame, self.last_analysis.get('emotion') if self.last_analysis else None)

            with self.lock:
                self.frame = frame

    def _draw_emotion_bar_graph(self, frame, emotions):
        if emotions is None:
            return frame
        graph_w = 250
        graph_h = frame.shape[0]
        bar_area = np.zeros((graph_h, graph_w, 3), dtype=np.uint8)
        max_bar_width = graph_w - 120
        bar_height = 40
        spacing = 10
        y_offset = 20
        for emotion in EMOTION_LIST:
            value = emotions.get(emotion, 0)
            bar_width = int(max_bar_width * (value / 100))
            cv2.putText(bar_area, f"{emotion}: {value:.0f}%", (10, y_offset + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.rectangle(bar_area, (120, y_offset), (120 + bar_width, y_offset + bar_height), (0, 255, 0), -1)
            y_offset += bar_height + spacing
        frame[:, frame.shape[1]-graph_w:frame.shape[1]] = bar_area
        return frame

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            ret, jpeg = cv2.imencode('.jpg', self.frame)
            if not ret:
                return None
            return jpeg.tobytes()

_detector = DetectorThread()

def start_detector():
    return _detector.start()

def stop_detector():
    return _detector.stop()

def get_frame_bytes():
    return _detector.get_frame()

def is_running():
    with _detector.lock:
        return _detector.running
