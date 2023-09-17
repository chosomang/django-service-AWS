from M_logs import views
from django.urls import path

urlpatterns = [
    path('<type>/', views.log_view),
]
