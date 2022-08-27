"""
WSGI config for friend_reminder project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'friend_reminder.settings')

if os.environ.get('SERVE_STATIC') == 'True':
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()
