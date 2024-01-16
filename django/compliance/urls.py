from django.urls import include, path
from django.conf import settings
from . import views
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from django.views.decorators.clickjacking import xframe_options_sameorigin

@xframe_options_sameorigin
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)

urlpatterns = [
    # Compliance Lists
    path('lists/', views.compliance_lists_view),
    path('lists/<compliance_type>/', views.compliance_lists_view),
    path('lists/<compliance_type>/modify/', views.compliance_lists_modify),
    path('lists/<compliance_type>/details/', views.compliance_lists_detail_view),
    path('lists/<compliance_type>/download/', views.download_compliance_report),
    path('lists/evidence/file/<action_type>/', views.compliance_lists_file_action),
    
    # Asset Management
    path('assets/', views.assets_view),
    path('assets/<asset_type>/', views.assets_view),
    path('assets/table/<action_type>/', views.assets_table),
    path('assets/<asset_type>/<action_type>/', views.assets_action),
    
    # Evidence Management
    path('evidence/', views.evidence_view),
    path('evidence/data/<action_type>/', views.evidence_data_action),
    path('evidence/file/<action_type>/', views.evidence_file_action),
    path('evidence/compliance/<action_type>/', views.evidence_related_compliance),    
    path('evidence/<product_name>/<data_name>/', views.evidence_data_detail_view),

    # Policy Management
    path('policy/', views.policy_view),
    path('policy/<action_type>/', views.policy_action),
    path('policy/data/<action_type>/', views.policy_data_action),
    path('policy/<policy_type>/<data_type>/', views.policy_data_view),
    path('policy/<policy_type>/<data_type>/file/<action_type>/', views.policy_data_file_action),

    # File Preview
    path('file/preview/<evidence_type>/', views.data_file_preview),
    #-------------------------------------------------------------------------------------

    path('integration/', views.integration),
    path('integration_add/', views.add_integration),

    re_path(r'^media/(?P<path>.*)$', protected_serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]