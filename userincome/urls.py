from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='income'),
    path('add-income', views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.income_edit, name='income-edit'),
    path('income-delete/<int:id>', views.delete_income, name='income-delete'),
    path('search-income', csrf_exempt(views.search_income), name='search-income'),
    path('income_source_summary',views.income_source_summary, name="income_source_summary"),
    path('export_pdfincome',views.export_pdfincome, name="export-pdfincome"),

]

export_url=[
     path('statsincome',views.statsincome_view, name="statsincome"),
     path('export_csvincome',views.export_csvincome, name="export-csvincome"),
     path('export_excelincome',views.export_excelincome, name="export-excelincome"),
]


urlpatterns+=export_url