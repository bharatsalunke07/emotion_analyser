from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from . import detection
import time
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'detector_app/index.html')

def gen_mjpeg():
    while True:
        frame = detection.get_frame_bytes()
        if frame is None:
            time.sleep(0.05)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(gen_mjpeg(), content_type='multipart/x-mixed-replace; boundary=frame')

@csrf_exempt
def start_detection(request):
    try:
        started = detection.start_detector()
        return JsonResponse({'started': started})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def stop_detection(request):
    stopped = detection.stop_detector()
    return JsonResponse({'stopped': stopped})

def status(request):
    return JsonResponse({'running': detection.is_running()})
