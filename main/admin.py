from django.contrib import admin

from main.models import Friend, UserPreferences

admin.site.register([UserPreferences, Friend])
# Register your models here.
