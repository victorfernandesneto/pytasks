from django.db import models
from datetime import datetime


class Task(models.Model):
    task_name = models.CharField(max_length=200)
    deadline = models.DateTimeField(default=datetime.today(), blank=False)
    user = models.CharField(max_length=100)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.task_name

