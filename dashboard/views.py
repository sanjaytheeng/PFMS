from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render,redirect
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime, timedelta

from expenses.models import Expense
from userincome.models import UserIncome
from django.contrib.auth.models import User
from django.http import JsonResponse
from userpreferences.models import UserPreference
from authentication.decorators import verify_premium

@login_required(login_url="/authentication/login")
@verify_premium
def dashboard_index(request):
    # Fetch user-specific data
    expenses = Expense.objects.filter(owner=request.user)
    income = UserIncome.objects.filter(owner=request.user)

    # Calculate metrics
    total_expenses = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
    total_income = income.aggregate(Sum("amount"))["amount__sum"] or 0

    balance = total_income - total_expenses
    expense_by_category = list(
        expenses.values("category").annotate(total=Sum("amount")).order_by("-total")
    )
    income_by_source = list(
        income.values("source").annotate(total=Sum("amount")).order_by("-total")
    )

    # Calculate trend data for the last 6 months
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    trend_data = []

    for i in range(6):
        month_start = start_date + timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)

        month_expenses = (
            expenses.filter(date__range=[month_start, month_end]).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
        month_income = (
            income.filter(date__range=[month_start, month_end]).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )

        trend_data.append(
            {
                "date": month_start.strftime("%B"),
                "income": month_income,
                "expenses": month_expenses,
            }
        )

    context = {
        "total_expenses": total_expenses,
        "total_income": total_income,
        "expense_by_category": json.dumps(expense_by_category, cls=DjangoJSONEncoder),
        "income_by_source": json.dumps(income_by_source, cls=DjangoJSONEncoder),
        "trend_data": json.dumps(trend_data, cls=DjangoJSONEncoder),
        "balance":balance,
    }

    return render(request, "dashboard/dashboard.html", context)

from django.utils import timezone
from django.contrib import messages
from icecream import ic

def payment_success(request):

    from datetime import timedelta
    from datetime import date
    from django.urls import reverse_lazy
    date_now = date.today()

    user = request.user
    ic(user)
    preference = UserPreference.objects.get(user = user)
    ic(preference)
    preference.premium = True
    preference.subscription_until = (date_now+timedelta(30))  
    preference.save()
    messages.success(request,"Subscribed Successfully")
    return redirect(reverse_lazy("dashboard_index"))

def payment_failure(request):
    return render(request, 'result/failure.html')


def unpaid(request):    
    from django.http import HttpResponse

    return render(request,"unpaid/subscribe.html")