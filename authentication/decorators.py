from userpreferences.models import UserPreference
from django.urls import reverse_lazy
from django.shortcuts import redirect
from datetime import timedelta,date

def verify_premium(view_func):
    def wrapper(request, *args, **kwargs):
        # code to be executed before the view
        user_preference = UserPreference.objects.get(user = request.user)
        premium = user_preference.premium
        time = user_preference.subscription_until
        now = date.today()
        
        if premium == False:
            return redirect (reverse_lazy("unpaid"))
        if time < now:
            return redirect (reverse_lazy("unpaid"))

        response = view_func(request, *args, **kwargs)
        # code to be executed after the view
        return response
    return wrapper
