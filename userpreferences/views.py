from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    with open(file_path, 'r')as json_file:
                data = json.load(json_file)
                for k, v in data.items():
                    currency_data.append({'name': k, 'values':v})

    exists= UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None

    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)

    if request.method=='GET':
        

        return render(request, 'preferences/index.html',{'currencies': currency_data, 'user_preferences':user_preferences})
    else:
        currency = request.POST['currency']

        if exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved.')
        return render(request, 'preferences/index.html',{'currencies': currency_data, 'user_preferences':user_preferences})

# @csrf_exempt
# def toggle_theme(request):
#     if request.method == 'POST':
#         import json
#         data = json.loads(request.body)
#         request.session['theme'] = data['theme']
#         return JsonResponse({'status': 'Theme updated'})

#     # GET request, return current theme
#     theme = request.session.get('theme', 'light')
#     return JsonResponse({'theme': theme})
