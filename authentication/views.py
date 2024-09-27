from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout
from userpreferences.models import UserPreference
from icecream import ic

# Create your views here.


class RegisterView(View):
    def get(self, request):
        return render(request, "authentication/register.html")

    def post(self, request):
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        context = {"fieldValues": request.POST}

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password too short")
                    return render(request, "authentication/register.html", context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = True
                user.save()
                user_prefs = UserPreference.objects.create(user = user)
                ic(user_prefs)
                messages.success(request, "Account Successfully created")
                return render(request, "authentication/register.html")

        return render(request, "authentication/register.html")


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data["username"]
        if not str(username).isalnum():
            return JsonResponse(
                {
                    "username_error": "Username should only contain alphanumeric characters."
                },
                status=400,
            )
        
        user = User.objects.filter(username = username)
        if user:
           
            
            return JsonResponse(
                {"username_error": "Sorry username in use, please choose another one."},
                status=409,
            )
        return JsonResponse({"username_valid": True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data["email"]
        if not validate_email(email):
            return JsonResponse({"email_error": "Email is invalid."}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"email_error": "Sorry email in use, please choose another one."},
                status=409,
            )
        return JsonResponse({"email_valid": True})


class LoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        print(username)
        print(password)

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    print("login successfull")

                    from datetime import date
                    now = date.today()

                    userpreference ,_= UserPreference.objects.get_or_create(user = user)

                    if userpreference.premium !=True:
                        messages.error(request,"No Premium")
                        return redirect(reverse_lazy("unpaid"))
                    
                    if userpreference.subscription_until<now:
                        messages.error(request,message="Subscription Finished Please subscrabie")
                        return redirect(reverse_lazy('unpaid'))
                    
                    
                    return redirect(reverse_lazy("dashboard_index"))
                messages.error(
                    request,
                    "Account is not active, please check your email",
                )
                return render(request, "authentication/login.html")
            messages.error(request, "Invalid username or password")
            return render(request, "authentication/login.html")

        messages.error(request, "Please fill in all fields")
        return render(request, "authentication/login.html")


def logout_user(request):
    logout(request)
    return redirect(reverse_lazy("login"))
