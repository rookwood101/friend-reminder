import json
import time
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from guest_user.decorators import allow_guest_user, regular_user_required
import stripe
from webpush import send_user_notification

from main.forms import FriendCreateForm, FriendEditForm
from main.models import Friend, UserPreferences

class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


@allow_guest_user
@require_http_methods(['GET', 'POST'])
def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_anonymous:
        return HttpResponseSeeOther('/accounts/login')
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

                return HttpResponseSeeOther(f'/friend/{friend.pk}')

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
        return HttpResponseSeeOther('/')
    elif request.method == 'POST':
        friend_form = FriendEditForm(request.POST, instance=friend)
        if friend_form.is_valid():
            friend_form.save()
            return HttpResponseSeeOther(request.META.get('HTTP_REFERER', f'/friend/{friend.pk}'))


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
    return HttpResponseSeeOther(request.META.get('HTTP_REFERER', f'/friend/{friend.pk}'))


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
    return HttpResponseSeeOther('/')


@regular_user_required
@login_required
@require_http_methods(['GET'])
def subscribe(request: HttpRequest) -> HttpResponse:
    return render(request, 'subscribe.html', {})


@regular_user_required
@login_required
@require_http_methods(['POST'])
def create_checkout_session(request: HttpRequest) -> HttpResponse:
    preferences: UserPreferences = UserPreferences.get_or_create(request.user)
    if (
        preferences.subscription_status == UserPreferences.SubscriptionStatus.ACTIVE
        or preferences.subscription_status == UserPreferences.SubscriptionStatus.PENDING_PAYMENT
    ):
        return HttpResponseSeeOther('/subscribe')

    prices = stripe.Price.list(
        lookup_keys=['friend-reminder-unlimited'],
        expand=['data.product'],
        limit=1,
    )

    checkout_session = stripe.checkout.Session.create(
        client_reference_id=request.user.pk,
        line_items=[
            {
                'price': prices.data[0].id,
                'quantity': 1,
            },
        ],
        mode='subscription',
        # build_absolute_uri encodes curly braces such that stripe does not substitute the checkout session id
        success_url=request.build_absolute_uri('/subscription-success') + '?checkout_session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/subscribe'),
    )
    return HttpResponseSeeOther(checkout_session.url)


@regular_user_required
@login_required
@require_http_methods(['GET'])
def checkout_cancelled(request: HttpRequest) -> HttpResponse:
    return HttpResponse('Checkout cancelled')


@regular_user_required
@login_required
@require_http_methods(['GET'])
def subscription_success(request: HttpRequest) -> HttpResponse:
    checkout_session = stripe.checkout.Session.retrieve(request.GET['checkout_session_id'])
    if not checkout_session or int(checkout_session.client_reference_id) != request.user.pk:
        return HttpResponseBadRequest('Invalid checkout session id')

    preferences: UserPreferences = UserPreferences.get_or_create(request.user)
    preferences.stripe_customer_id = checkout_session.customer

    if checkout_session.payment_status == 'paid':
        preferences.subscription_status = UserPreferences.SubscriptionStatus.ACTIVE
    else:
        preferences.subscription_status = UserPreferences.SubscriptionStatus.PENDING_PAYMENT
    preferences.save()
    return HttpResponseSeeOther('/subscribe')


@csrf_exempt
@require_http_methods(['POST'])
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    signature = request.headers.get('stripe-signature')
    event: stripe.Event = stripe.Webhook.construct_event(payload=request.body, sig_header=signature, secret=webhook_secret)
    # Get the type of webhook event sent - used to check the status of PaymentIntents.
    if event.type == 'checkout.session.completed':
        checkout_session: stripe.checkout.Session = event.data.object
        preferences: UserPreferences = UserPreferences.get_or_create(user_pk=checkout_session.client_reference_id)
        preferences.stripe_customer_id = checkout_session.customer
        preferences.save()
    elif event.type == 'customer.subscription.created':
        subscription = event.data.object
        preferences = get_object_or_404(UserPreferences, stripe_customer_id=subscription.customer)
        preferences.subscription_status = UserPreferences.SubscriptionStatus.ACTIVE
        preferences.save()

    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        preferences = get_object_or_404(UserPreferences, stripe_customer_id=subscription.customer)
        preferences.subscription_status = UserPreferences.SubscriptionStatus.INACTIVE
        preferences.save()
    else:
        print(f'Unhandled webhook notification: {event.type}')


    return HttpResponse()


@regular_user_required
@login_required
@require_http_methods(['POST'])
def create_portal_session(request: HttpRequest) -> HttpResponse:
    preferences: UserPreferences = UserPreferences.get_or_create(request.user)
    if preferences.stripe_customer_id is None:
        return HttpResponseSeeOther('/subscribe')

    portal_session = stripe.billing_portal.Session.create(
        customer=preferences.stripe_customer_id,
        return_url=request.build_absolute_uri('/'),
    )
    return HttpResponseSeeOther(portal_session.url)
