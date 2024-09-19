from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import tempfile
from django.db.models import Sum

# Create your views here.
from authentication.decorators import verify_premium

@login_required(login_url="/authentication/login")
@verify_premium
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 4)
    page_number = request.GET.get("page")
    page_obj = Paginator.get_page(paginator, page_number)
    userpref, created = UserPreference.objects.get_or_create(
        user=request.user, defaults={"currency": "NPR - Nepali Rupees"}
    )
    print(userpref)

    context = {
        "expenses": expenses,
        "page_obj": page_obj,
        "currency": userpref.currency,
    }
    return render(request, "expenses/index.html", context)


@login_required(login_url="/authentication/login")
@verify_premium

def add_expense(request):
    categories = Category.objects.all()
    context = {"categories": categories, "values": request.POST}
    if request.method == "GET":
        return render(request, "expenses/add_expense.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Please enter an amount")
            return render(request, "expenses/add_expense.html", context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "expenses/add_expense.html", context)

        expense_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.datetime.today().date()

        if expense_date > today:
            messages.error(request, "The date cannot be tomorrow or any future date.")
            return render(request, "expenses/add_expense.html", context)

    Expense.objects.create(
        owner=request.user,
        amount=amount,
        description=description,
        date=date,
        category=category,
    )
    messages.success(request, "Expense added successfully")

    return redirect("expenses")


@login_required(login_url="/authentication/login")
@verify_premium

def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {"expense": expense, "values": expense, "categories": categories}
    if request.method == "GET":
        return render(request, "expenses/edit-expense.html", context)
    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Please enter an amount")
            return render(request, "expenses/edit-expense.html", context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "edit-expense.html", context)

        # Validate the date
        try:
            expense_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format")
            return render(request, "expenses/edit-expense.html", context)

        today = datetime.datetime.today().date()

        if expense_date > today:
            messages.error(request, "The date cannot be a future date.")
            return render(request, "expenses/edit-expense.html", context)

    Expense.objects.create(
        owner=request.user,
        amount=amount,
        description=description,
        date=date,
        category=category,
    )

    expense.owner = request.user
    expense.amount = amount
    expense.date = date
    expense.description = description
    expense.save()
    messages.success(request, "Expense Updated successfully")

    return redirect("expenses")


@login_required(login_url="/authentication/login")
@verify_premium

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense deleted successfully")
    return redirect("expenses")


@login_required(login_url="/authentication/login")
@verify_premium

def search_expenses(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")

        expenses = (
            Expense.objects.filter(amount__istartswith=search_str, owner=request.user)
            | Expense.objects.filter(date__istartswith=search_str, owner=request.user)
            | Expense.objects.filter(
                description__icontains=search_str, owner=request.user
            )
            | Expense.objects.filter(category__icontains=search_str, owner=request.user)
        )

        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url="/authentication/login")
@verify_premium

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(
        owner=request.user, date__gte=six_months_ago, date__lte=todays_date
    )
    finalrep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount

        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({"expense_category_data": finalrep}, safe=False)


@login_required(login_url="/authentication/login")
@verify_premium

def stats_view(request):
    expense = Expense.objects.filter(owner_id=request.user.id)
    pref = UserPreference.objects.filter(user = request.user).first()
    context = {
        "expenses": expense,
        "pref": pref,
        "total": expense.aggregate(total=Sum("amount"))["total"],
    }
    return render(request, "expenses/stats.html", context=context)


@login_required(login_url="/authentication/login")
@verify_premium

def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=Expenses" + str(datetime.datetime.now()) + ".csv"
    )
    writer = csv.writer(response)
    writer.writerow(["Amount", "Description", "Category", "Date"])
    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow(
            [expense.amount, expense.description, expense.category, expense.date]
        )
    return response


@login_required(login_url="/authentication/login")
@verify_premium

def export_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        "attachment; filename=Expenses" + str(datetime.datetime.now()) + ".xls"
    )
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Expenses")
    row_num = 0
    columns = ["Amount", "Description", "Category", "Date"]
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list(
        "amount", "description", "category", "date"
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response


@login_required(login_url="/authentication/login")
@verify_premium

def export_pdf(request):
    # Get expenses for the current user
    expenses = Expense.objects.filter(owner=request.user)

    # Calculate the total amount
    total = expenses.aggregate(Sum("amount"))["amount__sum"] or 0

    # Create a response object with PDF content
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename=Expenses_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf'
    )

    # Create the PDF object, using the HttpResponse as its "file."
    pdf = SimpleDocTemplate(response, pagesize=A4)

    # Container for the 'Flowable' objects
    elements = []

    # Set up styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    # Add title
    elements.append(Paragraph("Expenses Report", title_style))

    # Create table data with expenses
    data = [["Date", "Description", "Category", "Amount"]]
    for expense in expenses:
        data.append(
            [
                expense.date.strftime("%Y-%m-%d"),
                expense.description,
                expense.category if expense.category else "",
                f"{expense.amount:.2f}",
            ]
        )

    # Create the table
    table = Table(data, colWidths=[1.5 * inch, 3 * inch, 1.5 * inch, 1.5 * inch])

    # Style the table
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    # Add table to the elements
    elements.append(table)

    # Define a custom style with bold text and left alignment
    custom_style = ParagraphStyle(
        name="CustomStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=TA_RIGHT,
        leftIndent=0,
        borderPadding=2,
    )
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total: {total:.2f}", custom_style))
    # Build the PDF
    pdf.build(elements)

    return response
