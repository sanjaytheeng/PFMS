from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# from weasyprint import HTML
import tempfile
from django.db.models import Sum

from authentication.decorators import verify_premium


# Create your views here.


@login_required(login_url="/authentication/login")
@verify_premium
def index(request):
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 4)
    page_number = request.GET.get("page")
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        "income": income,
        "page_obj": page_obj,
        "currency": currency,
    }
    return render(request, "income/index.html", context)


@login_required(login_url="/authentication/login")
@verify_premium

def add_income(request):
    sources = Source.objects.all()
    context = {"sources": sources, "values": request.POST}
    if request.method == "GET":
        return render(request, "income/add_income.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Please enter an amount")
            return render(request, "income/add_income.html", context)

        description = request.POST["description"]
        date = request.POST["income_date"]
        source = request.POST["source"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "income/add_income.html", context)
        
        income_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.datetime.today().date()
        
        if income_date > today:
            messages.error(request, "The date cannot be tomorrow or any future date.")
            return render(request, "income/add_income.html", context)


    UserIncome.objects.create(
        owner=request.user,
        amount=amount,
        description=description,
        date=date,
        source=source,
    )
    messages.success(request, "Income added successfully")

    return redirect("income")


@login_required(login_url="/authentication/login")
@verify_premium

def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {"income": income, "values": income, "sources": sources}
    if request.method == "GET":
        return render(request, "income/edit-income.html", context)
    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Please enter an amount")
            return render(request, "income/edit-income.html", context)

        description = request.POST["description"]
        date = request.POST["income_date"]
        source = request.POST["source"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "edit-expense.html", context)
        
        # Validate the date
        try:
            income_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format")
            return render(request, "income/edit-income.html", context)
        
        today = datetime.datetime.today().date()

        if income_date > today:
            messages.error(request, "The date cannot be a future date.")
            return render(request, "income/edit-income.html", context)
        

    income.amount = amount
    income.date = date
    income.description = description
    income.save()
    messages.success(request, "Income Updated successfully")

    return redirect("income")


@login_required(login_url="/authentication/login")
@verify_premium

def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, "Income deleted successfully")
    return redirect("income")


@login_required(login_url="/authentication/login")
@verify_premium

def search_income(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")

        income = (
            UserIncome.objects.filter(
                amount__istartswith=search_str, owner=request.user
            )
            | UserIncome.objects.filter(
                date__istartswith=search_str, owner=request.user
            )
            | UserIncome.objects.filter(
                description__icontains=search_str, owner=request.user
            )
            | UserIncome.objects.filter(
                source__icontains=search_str, owner=request.user
            )
        )

        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url="/authentication/login")
@verify_premium

def income_source_summary(request):
    # Get today's date and the date six months ago
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    
    # Filter incomes within the last six months for the logged-in user
    incomes = UserIncome.objects.filter(
        owner=request.user, date__gte=six_months_ago, date__lte=todays_date
    )
    
    # Prepare data structures to store labels and amounts
    finalrep = {}

    def get_source(income):
        return income.source

    # Get a unique list of income sources
    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        # Aggregate the sum of income amounts per source
        amount = 0
        filtered_by_source = incomes.filter(source = source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in incomes:
        for y in source_list:
            finalrep[y] = get_income_source_amount(y)

    return JsonResponse({'income_source_data': finalrep}, safe=False)


@login_required(login_url="/authentication/login")
@verify_premium
def statsincome_view(request):
    incomes = UserIncome.objects.filter(owner_id=request.user.id)
    pref = UserPreference.objects.filter(user = request.user).first()

    context = {
        "incomes": incomes,
        "pref": pref,
        "total":incomes.aggregate(total=Sum('amount'))['total']
    }
    return render(request, "income/statsincome.html", context=context)


@login_required(login_url="/authentication/login")
@verify_premium

def export_csvincome(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=Income_" + str(datetime.datetime.now()) + ".csv"
    )

    writer = csv.writer(response)
    writer.writerow(["Amount", "Description", "Source", "Date"])

    income = UserIncome.objects.filter(owner=request.user)
    for inc in income:
        writer.writerow([inc.amount, inc.description, inc.source, inc.date])

    return response


@login_required(login_url="/authentication/login")
@verify_premium

def export_excelincome(request):
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        "attachment; filename=Income_" + str(datetime.datetime.now()) + ".xls"
    )

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Income")

    row_num = 0
    columns = ["Amount", "Description", "Source", "Date"]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = UserIncome.objects.filter(owner=request.user).values_list(
        "amount", "description", "source", "date"
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response

@login_required(login_url="/authentication/login")
@verify_premium

def export_pdfincome(request):
    # Get income data for the current user
    income_data = UserIncome.objects.filter(owner=request.user)

    # Calculate the total amount
    total = income_data.aggregate(Sum("amount"))["amount__sum"] or 0

    # Create a response object with PDF content
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename=Income_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf'
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
    elements.append(Paragraph("Income Report", title_style))

    # Create table data with income information
    data = [["Date", "Description", "Source", "Amount"]]
    for income in income_data:
        data.append(
            [
                income.date.strftime("%Y-%m-%d"),
                income.description,
                income.source if income.source else "",
                f"{income.amount:.2f}",
            ]
        )

    # Create the table
    table = Table(data, colWidths=[1.5 * inch, 3 * inch, 3 * inch, 1.5 * inch])

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

    # Define a custom style with bold text and right alignment
    custom_style = ParagraphStyle(
        name="CustomStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=TA_RIGHT,
        leftIndent=0,
        borderPadding=2,
    )

    # Add total amount paragraph
    elements.append(Spacer(1, 12))  # Add some space before the total
    elements.append(Paragraph(f"Total Income: {total:.2f}", custom_style))

    # Build the PDF
    pdf.build(elements)

    return response
