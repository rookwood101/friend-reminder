from django.db import models
from django.contrib.auth.models import User

class Friend(models.Model):
    name = models.TextField()
    remind_period_days = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    friend_of = models.ForeignKey(User, on_delete=models.CASCADE)
