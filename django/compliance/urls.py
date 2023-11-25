from django.urls import include, path
from . import views


urlpatterns = [
    path('index/', views.compliance_view),
    path('compliance/', views.compliance_view),
    #path('report_month/', views.report_month_view, name='[Teiren] 월간 위협 보고서'),
    path('lists/', views.lists_view),
    path('lists_2/', views.lists_view_2),
    path('evidence_cate/', views.evidence_cate),
    path('evidence_cate_add/', views.evidence_cate_add),
    path('evidence_cate_del/', views.evidence_cate_del),
    path('evidence_data/', views.evidence_data),
    path('evidence_4/', views.evidence_view_4),
    #path('<at>/evidence_data_add/', views.evidence_data_add),
    path('evidence_data_add/', views.evidence_data_add),
    path('evidence_data_add_result/', views.evidence_data_add_result),
    path('evidence_data_del/', views.evidence_data_del),
    path('evidence_get_compliance', views.evidence_get_compliance),
    path('evidence_get_compliance_articles', views.evidence_get_compliance_articles)

 ]