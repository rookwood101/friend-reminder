from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from webpush import send_user_notification

from main.forms import FriendForm
from main.models import Friend


@login_required
@require_http_methods(['GET', 'POST'])
def home(request: HttpRequest) -> HttpResponse:
    friends = Friend.objects.filter(friend_of=request.user)
    friend_form = FriendForm()

    if request.method == 'POST':
        form_name = request.POST['form_name']
        if form_name == 'Friend':
            friend_form = FriendForm(request.POST)
            if friend_form.is_valid():
                friend: Friend = friend_form.save(commit=False)
                friend.friend_of = request.user
                friend.update_next_reminder()

                return HttpResponseRedirect('/')

    return render(request, 'home.html', {
        'friends': friends,
        'friend_form': friend_form,
    })


@login_required
@require_http_methods(['POST'])
def test_push(request: HttpRequest) -> HttpResponse:
    payload = {
        "head": "Welcome!",
        "body": "Hello World",
        "icon": "https://i.imgur.com/dRDxiCQ.png",
        "url": request.build_absolute_uri('/'),
    }
    send_user_notification(user=request.user, payload=payload, ttl=1000)
    return HttpResponseRedirect('/')
