
# pylint: disable=wrong-import-position
from video_analyzer.analyzer.ObjectCounter import ObjectCounter
import cv2
import json
import os
from django.utils import timezone


def analyze(video, model, uid):
    print("start")
    model_obj = model(uid=uid, processed="0", frames_processed="0",
                      frames_left="null", frames_rate="0", data="{}", status="Waiting...", start_time=timezone.now())
    model_obj.save()
    if not video:
        model_obj.status = "Failed"
        model_obj.end_time = timezone.now()
        model_obj.save()
        return None

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        model_obj.status = "Failed"
        model_obj.end_time = timezone.now()
        model_obj.save()
        return None
    model_obj.status = "Processing..."
    model_obj.save()
    retval, frame = cap.read()
    detection_interval = 10
    mcdf = 2
    mctf = 3
    counting_lines = [{'label': 'A', 'line': [(0, 600), (1600, 600)]}]
    f_height, f_width, _ = frame.shape
    droi = [(0, 0), (f_width, 0), (f_width, f_height), (0, f_height)]

    object_counter = ObjectCounter(frame, mcdf, mctf, droi,
                                   detection_interval, counting_lines)

    frames_count = round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_processed = 0
    last_known_data = None

    try:
        while retval:
            object_counter.count(frame)
            retval, frame = cap.read()
            new_data = object_counter.get_counts()
            _timer = cv2.getTickCount()
            processing_frame_rate = round(
                cv2.getTickFrequency() / (cv2.getTickCount() - _timer), 2)
            frames_processed += 1
            if last_known_data != str(new_data):
                last_known_data = str(new_data)
                model_obj.processed = round(
                    (frames_processed / frames_count) * 100, 2)
                model_obj.frames_processed = frames_processed
                model_obj.frames_left = frames_count - frames_processed
                model_obj.frames_rate = processing_frame_rate
                model_obj.data = json.dumps(new_data)
                model_obj.status = "Analyzing..."
                model_obj.save()

    finally:
        cap.release()
        model_obj.status = "Completed" if frames_count - \
            frames_processed == 0 else "Failed"
        model_obj.end_time = timezone.now()
        model_obj.save()
        print("end")
        os.remove(video)

    return True
