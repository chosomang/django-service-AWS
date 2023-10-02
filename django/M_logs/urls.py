from M_logs import views
from django.urls import path

urlpatterns = [
    path('<cloud>/', views.log_view),
]
