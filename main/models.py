from datetime import timedelta
from typing_extensions import Self
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Friend(models.Model):
    name = models.TextField()
    remind_period_days = models.PositiveIntegerField()
    friend_of = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def next_reminder(self) -> timedelta:
        remind_period = timedelta(days=self.remind_period_days)
        since_creation: timedelta = timezone.now() - self.created_at
        since_last_reminder: timedelta = since_creation % remind_period
        next_reminder =  remind_period - since_last_reminder
        return next_reminder

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.TextField()

    @staticmethod
    def get_or_create(user: User) -> Self:
        preferences: UserPreferences = UserPreferences.objects.filter(user=user).first()
        if preferences:
            return preferences
        else:
            return UserPreferences(user=user)
