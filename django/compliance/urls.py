from django.urls import include, path
from . import views


urlpatterns = [
    path('index/', views.compliance_view),
    path('compliance/', views.compliance_view),
    #path('report_month/', views.report_month_view, name='[Teiren] 월간 위협 보고서'),
    path('lists/', views.lists_view),
    path('lists_2/', views.lists_view_2),
    path('evidence/data/', views.data),
    path('evidence/data_add/', views.add_data),
    path('evidence/data_del/', views.del_data),
    path('evidence/file/', views.file),
    path('evidence_4/', views.evidence_view_4),
    #path('<at>/evidence_data_add/', views.evidence_data_add),
    path('evidence/file_add/', views.add_file),
    path('evidence/file_add_func/', views.add_file_func),
    path('evidence/file_del/', views.del_file),
    path('evidence_get_compliance', views.evidence_get_compliance),
    path('evidence/get_compliance_articles', views.get_compliance_articles),
]