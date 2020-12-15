from django.db import models
import uuid
# Create your models here.


class Video(models.Model):
    uid = models.TextField(max_length=255, default=uuid.uuid4())
    processed = models.TextField(max_length=255, default="0")
    frames_processed = models.TextField(max_length=255, default="0")
    frames_left = models.TextField(max_length=255, default="0")
    frames_rate = models.TextField(max_length=255, default="0")
    data = models.TextField(max_length=255, default="{}")
    status = models.TextField(max_length=255, default="Unknown")
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def get_data(self):
        return {"uid": self.uid, "processed": self.processed, "frames_processed": self.frames_processed,
                "frames_left": self.frames_left, "frames_rate": self.frames_rate, "data": self.data, "status": self.status,
                "start_time": self.start_time, "end_time": self.end_time}
