from . import views
from django.urls import path
# from .views import toggle_theme

urlpatterns = [
    path('', views.index, name='preferences'),
    # path('toggle-theme/', toggle_theme, name='toggle-theme')
]
