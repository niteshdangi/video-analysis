

def get_bounding_boxes(frame):
    '''
    Run object detection algorithm and return a list of bounding boxes and other metadata.
    '''
    from video_analyzer.analyzer.detectors.yolo import get_bounding_boxes as gbb
    return gbb(frame)
