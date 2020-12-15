from django.http.response import HttpResponseRedirect
from analyzer.models import Video
from django.shortcuts import render
from threading import Thread
from video_analyzer.analyzer.main import analyze
import uuid
import os
from django.core.files.storage import FileSystemStorage

from django.conf import settings


class AnalyzerWorker(Thread):

    def __init__(self, video, model, uid):
        Thread.__init__(self)
        self.video = video
        self.model = model
        self.uid = uid

    def run(self):
        analyze(self.video, self.model, self.uid)


def home(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        uid = uuid.uuid4()
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.path(filename)
        worker = AnalyzerWorker(uploaded_file_url, Video, uid)
        worker.daemon = True
        worker.start()
        return HttpResponseRedirect("?id="+str(uid))
    elif request.method == "GET" and "id" in request.GET.keys():
        data = "Invalid ID"
        try:
            data = Video.objects.get(uid=request.GET['id']).get_data()
        except:
            pass
        return render(request, "index.html", {"video": [data]})
    data = []
    videos = Video.objects.all()
    for video in videos:
        data.append(video.get_data())
    return render(request, "index.html", {"video": data})
