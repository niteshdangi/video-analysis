
import cv2
from video_analyzer.analyzer.util.blob import Blob
from video_analyzer.analyzer.util.bounding_box import get_overlap
from video_analyzer.analyzer.util.object_info import generate_object_id


def _kcf_create(bounding_box, frame):
    '''
    Create an OpenCV KCF Tracker object.
    '''
    tracker = cv2.TrackerKCF_create()
    tracker.init(frame, tuple(bounding_box))
    return tracker


def get_tracker(bounding_box, frame):
    '''
    Fetch a tracker object based on the algorithm specified.
    '''
    return _kcf_create(bounding_box, frame)


def _remove_stray_blobs(blobs, matched_blob_ids, mcdf):
    '''
    Remove blobs that "hang" after a tracked object has left the frame.
    '''
    for blob_id, blob in list(blobs.items()):
        if blob_id not in matched_blob_ids:
            blob.num_consecutive_detection_failures += 1
        if blob.num_consecutive_detection_failures > mcdf:
            del blobs[blob_id]
    return blobs


def add_new_blobs(boxes, classes, confidences, blobs, frame, mcdf):
    '''
    Add new blobs or updates existing ones.
    '''
    matched_blob_ids = []
    for i, box in enumerate(boxes):
        _type = classes[i] if classes is not None else None
        _confidence = confidences[i] if confidences is not None else None
        _tracker = get_tracker(box, frame)

        match_found = False
        for _id, blob in blobs.items():
            if get_overlap(box, blob.bounding_box) >= 0.6:
                match_found = True
                if _id not in matched_blob_ids:
                    blob.num_consecutive_detection_failures = 0
                    matched_blob_ids.append(_id)
                blob.update(box, _type, _confidence, _tracker)

                blob_update_log_meta = {
                    'label': 'BLOB_UPDATE',
                    'object_id': _id,
                    'bounding_box': blob.bounding_box,
                    'type': blob.type,
                    'type_confidence': blob.type_confidence,
                }
                break

        if not match_found:
            _blob = Blob(box, _type, _confidence, _tracker)
            blob_id = generate_object_id()
            blobs[blob_id] = _blob

            blog_create_log_meta = {
                'label': 'BLOB_CREATE',
                'object_id': blob_id,
                'bounding_box': _blob.bounding_box,
                'type': _blob.type,
                'type_confidence': _blob.type_confidence,
            }

    blobs = _remove_stray_blobs(blobs, matched_blob_ids, mcdf)
    return blobs


def remove_duplicates(blobs):
    '''
    Remove duplicate blobs i.e blobs that point to an already detected and tracked object.
    '''
    for blob_id, blob_a in list(blobs.items()):
        for _, blob_b in list(blobs.items()):
            if blob_a == blob_b:
                break

            if get_overlap(blob_a.bounding_box, blob_b.bounding_box) >= 0.6 and blob_id in blobs:
                del blobs[blob_id]
    return blobs


def update_blob_tracker(blob, blob_id, frame):
    '''
    Update a blob's tracker object.
    '''
    success, box = blob.tracker.update(frame)
    if success:
        blob.num_consecutive_tracking_failures = 0
        blob.update(box)

    else:
        blob.num_consecutive_tracking_failures += 1

    return (blob_id, blob)
