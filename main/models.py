from datetime import date, datetime, time, timedelta
from typing import Optional
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
    log = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.friend_of.username}\'s friend {self.name}'

    def remind_tomorrow(self):
        today = timezone.now().date()
        self.next_reminder = today + timedelta(days=1)
        self.save()

    def send_reminder_if_applicable(self) -> bool:
        now = timezone.now()
        if now < datetime.combine(self.next_reminder, time(12, 0, 0), now.tzinfo):
            return False

        self.send_reminder()
        self.update_next_reminder()
        return True

    def send_reminder(self):
        payload = {
            'head': f'Contact {self.name} - Friend Reminder',
            'body': self.reminder_body(),
            'icon': 'https://i.imgur.com/8n3O62r.png',
            'url': f'https://friend-reminder.fly.dev/friend/{self.pk}',
        }
        # max ttl for some webpush servers is 28 days, it automatically gets rounded though
        seconds_to_store_if_undeliverable = int(
            timedelta(days=1) / timedelta(seconds=1)
        )
        send_user_notification(user=self.friend_of, payload=payload, ttl=seconds_to_store_if_undeliverable)
        print(f'Successfully sent reminder to {self.friend_of.username}')

    def reminder_body(self) -> str:
        return self.log.split('\n')[-1] + f'. Every {self.remind_period_days} days'
        
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
    class SubscriptionStatus(models.TextChoices):
        INACTIVE = 'Inactive'
        PENDING_PAYMENT = 'Pending Payment'
        ACTIVE = 'Active'

    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.TextField()
    stripe_customer_id = models.TextField(null=True, blank=False, unique=True)
    subscription_status = models.CharField(
        max_length=255,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INACTIVE,
    )

    def __str__(self):
        return f'{self.user.username}\'s preferences'

    @staticmethod
    def get_or_create(user: Optional[User] = None, user_pk: Optional[int] = None) -> Self:
        if user_pk:
            user = User.objects.get(pk=user_pk)
        preferences: UserPreferences = UserPreferences.objects.filter(user=user).first()
        if preferences:
            return preferences
        else:
            preferences = UserPreferences(user=user)
            preferences.save()
            return preferences
