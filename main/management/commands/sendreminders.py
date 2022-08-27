from django.core.management.base import BaseCommand, CommandError
from main.models import Friend

class Command(BaseCommand):
    help = 'Send reminders to all users\' friends if it is post due'

    def handle(self, *args, **options):
        reminders_sent = 0
        for friend in Friend.objects.all():
            friend.send_reminder_if_applicable()
            reminders_sent += 1
        print(f'Sent {reminders_sent} reminders.')
