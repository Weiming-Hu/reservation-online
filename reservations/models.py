from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import datetime


class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField("start time", default=now())
    end_time = models.DateTimeField("end time", default=now()+datetime.timedelta(hours=1))
    apply_time = models.DateTimeField("apply time", auto_now_add=True)
    display_name = models.CharField(max_length=20, default='undefined')
    
    def __str__(self):
        return self.user.get_username()
