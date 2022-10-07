from django.core.management.base import BaseCommand
from main.models import Friend
from pywebpush import WebPushException

class Command(BaseCommand):
    help = 'Send reminders to all users\' friends if it is post due'

    def handle(self, *args, **options):
        reminders_sent = 0
        for friend in Friend.objects.all():
            friend: Friend
            try:
                if friend.send_reminder_if_applicable():
                    reminders_sent += 1
            except WebPushException as e:
                print(f'Failed to send reminder for friend {friend.id}: {e.response.text}')
        print(f'Sent {reminders_sent} reminders.')
