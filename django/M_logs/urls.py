from django.urls import path
from . import views

urlpatterns = [
    # Log Management
    path('<cloud>/', views.log_view),
    path("modal/<cloud>/", views.log_modal)
]
