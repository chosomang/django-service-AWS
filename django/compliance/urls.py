from django.urls import include, path
from . import views


urlpatterns = [
    path('index/', views.compliance_view),
    path('compliance/', views.compliance_view),
    #path('report_month/', views.report_month_view, name='[Teiren] 월간 위협 보고서'),
    path('lists/', views.lists_view),
    path('lists_2/', views.lists_view_2),
    path('evidence/', views.evidence_view),
    path('evidence_2/', views.evidence_view_2),

]
