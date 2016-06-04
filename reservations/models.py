from django.db import models
from django.contrib.auth.models import User


class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField("start time")
    end_time = models.DateTimeField("end time")
    apply_time = models.DateTimeField("apply time", auto_now_add=True)
    
    def __str__(self):
        return self.user.get_username()