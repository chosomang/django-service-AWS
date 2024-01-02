from django.urls import include, path
from django.conf import settings
from . import views
from .src import delete, add, assets_data_add, assets_add, assets_data_delete, assets_delete, assets_file_add, assets_file_delete, assets_modify, assets_data_modify, assets_file_modify
from django.conf.urls.static import static

urlpatterns = [
    path('index/', views.compliance_view),
    path('compliance/', views.compliance_view),
    #path('report_month/', views.report_month_view, name='[Teiren] 월간 위협 보고서'),
    path('lists/', views.lists_view),
    path('lists_2/', views.lists_view_2),

    path('evidence/', views.get_evidence_data),
    path('evidence/data_add/', views.add_evidence_data),
    path('evidence/data_mod/', views.mod_evidence_data),
    path('evidence/data_del/', views.del_evidence_data),
    path('evidence/file/', views.get_evidence_file),
    path('evidence/file_add/', views.add_evidence_file),
    path('evidence/file_mod/', views.mod_evidence_file),
    path('evidence/file_del/', views.del_evidence_file),
    path('evidence/com_add/', views.add_com),
    path('evidence/get_compliance', views.get_compliance),
    path('evidence/get_version', views.get_version),
    path('evidence/get_article', views.get_article),
    path('evidence/get_product/', views.get_product),
    path('assets/', views.assets_view),

    path('delete/', delete.delete),
    path('add/', add.add),
    path('version_modify/', views.versionModify),

    path('integration/', views.integration),
    path('integration_add/', views.add_integration),

    path('policy/', views.get_policy),
    path('policy/file/', views.get_policy_data),
    path('policy/policy_add/', views.add_policy),
    path('policy/data_add/', views.add_policy_data),
    path('policy/data_mod/', views.mod_policy_data),
    path('policy/data_del/', views.del_policy_data),
    path('policy/file_add/', views.add_policy_file),
    path('policy/file_del/', views.del_policy_file)
,
    path('assets_change/', views.assetChange),
    path('assets_data_add/', assets_data_add.add),
    path('assets_add/', assets_add.add),
    path('assets_data_delete/', assets_data_delete.delete),
    path('assets_delete/', assets_delete.delete),
    path('file_view/', views.fileView),
    path('assets_file_add/', assets_file_add.add),
    path('assets_file_delete/', assets_file_delete.delete),
    path('assets_modify/', assets_modify.modify),
    path('assets_data_modify/', assets_data_modify.modify),
    path('assets_file_modify/', assets_file_modify.modify)

]