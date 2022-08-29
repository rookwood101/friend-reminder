from datetime import date, datetime, time, timedelta
from typing_extensions import Self
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from webpush import send_user_notification

class Friend(models.Model):
    name = models.TextField()
    remind_period_days = models.PositiveIntegerField()
    next_reminder = models.DateField()
    friend_of = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def send_reminder_if_applicable(self) -> bool:
        now = timezone.now()
        if now < datetime.combine(self.next_reminder, time(12, 0, 0), now.tzinfo):
            return False

        payload = {
            'head': 'Friend Reminder',
            'body': f'Contact {self.name} every {self.remind_period_days} days',
            'icon': 'https://i.imgur.com/8n3O62r.png',
            'url': 'https://friend-reminder.fly.dev/',
        }
        # max ttl for some webpush servers is 28 days, it automatically gets rounded though
        seconds_to_store_if_undeliverable = int(
            timedelta(days=1) / timedelta(seconds=1)
        )
        send_user_notification(user=self.friend_of, payload=payload, ttl=seconds_to_store_if_undeliverable)
        print(f'Successfully sent reminder to {self.friend_of.username}')

        self.update_next_reminder()
        return True
        
    def update_next_reminder(self):
        remind_period = timedelta(days=self.remind_period_days)
        today = timezone.now().date()
        if self.next_reminder is None:
            self.next_reminder = today + (remind_period / 2)
            self.save()
            return

        since_last_reminder: timedelta = today - self.next_reminder
        if since_last_reminder < timedelta(0):
            # next reminder is in future, no change needed
            return

        until_new_next_reminder: timedelta = remind_period - (since_last_reminder % remind_period)
        self.next_reminder =  today + until_new_next_reminder
        self.save()

    

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
