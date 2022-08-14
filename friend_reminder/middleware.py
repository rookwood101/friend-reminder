from urllib import parse
from django.utils import timezone

from main.models import UserPreferences


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.COOKIES.get('timezone')
        if tzname:
            tzname = parse.unquote(tzname)
            timezone.activate(tzname)
            preferences: UserPreferences = UserPreferences.objects.filter(user=request.user).first()
            if preferences.timezone != tzname:
                preferences.timezone = tzname
                preferences.save()
        else:
            timezone.deactivate()
        return self.get_response(request)
