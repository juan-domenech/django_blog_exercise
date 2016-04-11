from django.shortcuts import render, redirect
from django.contrib import messages, auth
from accounts.forms import UserRegistrationForm, UserLoginForm
from django.core.urlresolvers import reverse
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import datetime
import stripe
import arrow
import json
from django.http import HttpResponse
from models import User


stripe.api_key = settings.STRIPE_SECRET

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        print "POST",request.POST
        print "form",form

        if form.is_valid():
            try:
                customer = stripe.Customer.create(
                        email=form.cleaned_data['email'],
                        card=form.cleaned_data['stripe_id'],  # this is currently the card token/id
                        plan='REG_MONTHLY',
                )

                if customer:
                    user = form.save()  # save here to create the user and get its instance

                    # now we replace the card id with the actual user id for later
                    user.stripe_id = customer.id
                    user.subscription_end = arrow.now().replace(weeks=+4).datetime  # add 4 weeks from now
                    user.save()

                # check we saved correctly and can login
                user = auth.authenticate(email=request.POST.get('email'),
                                         password=request.POST.get('password1'))

                if user:
                    auth.login(request, user)
                    messages.success(request, "You have successfully registered")
                    return redirect(reverse('profile'))

                else:
                    messages.error(request, "unable to log you in at this time!")

            except stripe.error.CardError, e:
                form.add_error(request, "Your card was declined!")


        # if form.is_valid():
        #
        #     try:
        #         customer = stripe.Customer.create(
        #                 email=form.cleaned_data['email'],
        #                 card=form.cleaned_data['stripe_id'],  # this is currently the card token/id
        #                 plan='REG_MONTHLY',
        #         )
        #
        #         if customer:
        #             user = form.save()  # save here to create the user and get its instance
        #             # now we replace the card id with the actual user id for later
        #             user.stripe_id = customer.id
        #             user.subscription_end = arrow.now().replace(weeks= +4).datetime  # add 4 weeks from now
        #             user.save()
        #
        #     except stripe.error.CardError, e:
        #         messages.error(request, "Your card was declined!")
        #
        #     if customer.paid:
        #         form.save()
        #
        #         user = auth.authenticate(email=request.POST.get('email'),
        #                                  password=request.POST.get('password1'))
        #         if user:
        #             auth.login(request, user)
        #             messages.success(request, "You have successfully registered")
        #             return redirect(reverse('profile'))
        #         else:
        #             messages.error(request, "Unable to log you in at this time!")
        #     else:
        #         messages.error(request, "We were unable to take a payment with that card!")


    else:
        today = datetime.date.today()
        form = UserRegistrationForm(initial={'expiry_month': today.month,
                                             'expiry_year': today.year})

    args = {'form': form, 'publishable': settings.STRIPE_PUBLISHABLE}
    args.update(csrf(request))

    return render(request, 'register.html', args)



def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(email=request.POST.get('email'),
                                     password=request.POST.get('password'))

            if user is not None:
                auth.login(request, user)
                messages.error(request, "You have successfully logged in")
                return redirect(reverse('profile'))
            else:
                form.add_error(None, "Your email or password was not recognised")

    else:
        form = UserLoginForm()

    args = {'form': form}
    args.update(csrf(request))
    return render(request, 'login.html', args)



@login_required(login_url='/login/')
def profile(request):
    return render(request, 'profile.html')



def logout(request):
    auth.logout(request)
    messages.success(request, 'You have successfully logged out')
    # return render(request, 'index.html')
    return redirect('/')



@login_required(login_url='/accounts/login/')
def cancel_subscription(request):
    try:
        customer=stripe.Customer.retrieve(request.user.stripe_id)
        customer.cancel_subscription(at_period_end=True)
    except Exception,e:
        messages.error(request,e)
    return redirect('profile')



@csrf_exempt
def subscriptions_webhook(request):
    event_json = json.loads(request.body)

    if settings.DEBUG:
        print "***",event_json

    #Verify the event by fetching it from Stripe
    try:
        # firstly verify this is a real event generated by Stripe.com
        if not settings.DEBUG:
            event = stripe.Event.retrieve(event_json["id"])
        cust = event_json['object']['customer']
        paid = event_json['object']['paid']
        user = User.objects.get(stripe_id=cust)
        if user and paid:
            # add 4 weeks from now
            user.subscription_end = arrow.now().replace(weeks=+4).datetime
            user.save()

    except stripe.InvalidRequestError,e:
        return HttpResponse(status=404)
    return HttpResponse(status=200)

