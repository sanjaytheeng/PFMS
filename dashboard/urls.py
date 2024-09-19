from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard_index, name="dashboard_index"),
    path("payment-success", views.payment_success, name="payment-success"),
    path("payment-failed", views.payment_failure, name="payment-failed"),
    path("unpaid",views.unpaid,name="unpaid")

]
