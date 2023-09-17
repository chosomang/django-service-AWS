from django.urls import include, path
from . import views


urlpatterns = [
    path('index/', views.compliance_view),
    path('report/', views.report_view),
    path('report_month/', views.report_month_view, name='[Teiren] 월간 위협 보고서'),
]
