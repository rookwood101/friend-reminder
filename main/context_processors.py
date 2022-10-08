from typing import Dict
from django.http import HttpRequest

from main.models import UserPreferences


def user_preferences(request: HttpRequest) -> Dict:
    if request.user.is_anonymous:
        return {}
    else:
        return {
            'preferences': UserPreferences.get_or_create(request.user)
        }
