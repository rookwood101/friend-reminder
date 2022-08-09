from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from main.models import Friend


@login_required
def home(request: HttpRequest) -> HttpResponse:
    friends = Friend.objects.filter(friend_of=request.user)
    return render(request, 'home.html', {"friends": friends})

