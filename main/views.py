from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from guest_user.decorators import allow_guest_user, regular_user_required
from webpush import send_user_notification

from main.forms import FriendCreateForm, FriendEditForm
from main.models import Friend


@allow_guest_user
@require_http_methods(['GET', 'POST'])
def home(request: HttpRequest) -> HttpResponse:
    friends = Friend.objects.filter(friend_of=request.user)
    friend_form = FriendCreateForm()

    if request.method == 'POST':
        form_name = request.POST['form_name']
        if form_name == 'Friend':
            friend_form = FriendCreateForm(request.POST)
            if friend_form.is_valid():
                friend: Friend = friend_form.save(commit=False)
                friend.friend_of = request.user
                friend.update_next_reminder()

                return HttpResponseRedirect(f'/friend/{friend.pk}')

    return render(request, 'home.html', {
        'friends': friends,
        'friend_form': friend_form,
    })


@login_required
@require_http_methods(['GET', 'POST', 'DELETE'])
def friend(request: HttpRequest, id: int) -> HttpResponse:
    friend = get_object_or_404(Friend, pk=id)
    form = FriendEditForm(instance=friend)
    if friend.friend_of != request.user:
        return HttpResponseNotFound()

    if request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        friend.delete()
        return HttpResponseRedirect('/')
    elif request.method == 'POST':
        friend_form = FriendEditForm(request.POST, instance=friend)
        if friend_form.is_valid():
            friend_form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', f'/friend/{friend.pk}'))


    return render(request, 'friend.html', {
        'friend': friend,
        'form': form,
    })


@login_required
@require_http_methods(['POST'])
def remind_tomorrow(request: HttpRequest, id: int) -> HttpResponse:
    friend = get_object_or_404(Friend, pk=id)
    if friend.friend_of != request.user:
        return HttpResponseNotFound()
    friend.remind_tomorrow()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', f'/friend/{friend.pk}'))


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


@regular_user_required
@login_required
@require_http_methods(['GET'])
def subscribe(request: HttpRequest) -> HttpResponse:
    return render(request, 'subscribe.html', {})
