"""
URL configuration for MyCapital project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


@login_required
def redirect_to_dashboard(request):
    return HttpResponsePermanentRedirect(reverse_lazy("dashboard_index"))


urlpatterns = [
    path("",redirect_to_dashboard),
    path("dashboard/", include("dashboard.urls")),
    path("expenses/", include("expenses.urls")),
    path("authentication/", include("authentication.urls")),
    path("preferences/", include("userpreferences.urls")),
    path("income/", include("userincome.urls")),
    path("accountsetting/", include("accountsetting.urls")),
    path("admin/", admin.site.urls),
]
