from django.urls import include, path
from django.conf import settings
from . import views
from .src import delete, add
from django.conf.urls.static import static

urlpatterns = [
    # Compliance Lists
    path('lists/', views.compliance_lists_view),
    path('lists/<compliance_type>/', views.compliance_lists_view),
    path('lists/<compliance_type>/modify/', views.compliance_lists_modify),
    path('lists/<compliance_type>/details/', views.compliance_lists_detail_view),
    
    # Asset Management
    path('assets/', views.assets_view),
    path('assets/<asset_type>/', views.assets_view),
    path('assets/table/<action_type>/', views.assets_table),
    path('assets/<asset_type>/<action_type>/', views.assets_action),
    
    # Evidence Management
    path('evidence/', views.get_evidence_data),

    #-------------------------------------------------------------------------------------
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

    path('delete/', delete.delete),
    path('add/', add.add),
    

    path('integration/', views.integration),
    path('integration_add/', views.add_integration),

    path('policy/', views.get_policy),
    path('policy/file/', views.get_policy_data),
    path('policy/policy_add/', views.add_policy),
    path('policy/data_add/', views.add_policy_data),
    path('policy/data_mod/', views.mod_policy_data),
    path('policy/data_del/', views.del_policy_data),
    path('policy/file_add/', views.add_policy_file),
    path('policy/file_del/', views.del_policy_file),

]