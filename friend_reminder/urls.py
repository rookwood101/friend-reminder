"""friend_reminder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('friend/<int:id>', views.friend, name='friend'),
    path('friend/<int:id>/remind-tomorrow', views.remind_tomorrow, name='friend_remind-tomorrow'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('create-checkout-session', views.create_checkout_session, name='create-checkout-session'),
    path('checkout-cancelled', views.checkout_cancelled, name='checkout-cancelled'),
    path('subscription-success', views.subscription_success, name='subscription-success'),
    path('create-portal-session', views.create_portal_session, name='create-portal-session'),
    path('stripe-webhook', views.stripe_webhook, name='stripe-webhook'),
    path('webpush/', include('webpush.urls')),
    path('convert/', include("guest_user.urls")),
    path('test_push', views.test_push, name='test_push'),
]
