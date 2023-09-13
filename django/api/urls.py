
from django.urls import path, include
from api import views

# Views
urlpatterns = [
    # Dashboard
    path('', views.index),
    path('v1/', views.version)
]