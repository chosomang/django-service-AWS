
from django.urls import path
from TeirenSIEM import views, login, tests, ajax, auth
from TeirenSIEM.dashboard import gridstack
import TeirenSIEM.v1 as aws
# from webAPP.django.TeirenSIEM.v0 import dashboard_v0
from webAPP.django.TeirenSIEM.v1 import integrations


# Views
urlpatterns = [
    # Dashboard
    # path('dashboard/', views.dashboard),

    # Log Management
    # path('log/<type>/', views.log_view),

    # Integration
    # path('integration/', views.integration),
    # path('integration/<type>/', views.integration_type),

    # Risk Management
    ## alert
    # path('alert/<type>/', views.alert_view),
    # ## rules
    # path('rules/<type>/', views.rules_view),
    # ## visuals
    # path('visuals/<type>/', views.visuals_view),

    # # Settings
    # path('settings/<type>/', views.settings_view),

    # Compliance
    # path('compliance/compliance/', views.compliance),
    # path('compliance/report/', views.report),
    # path('compliance/report_month/', views.report_month, name='[Teiren] 월간 위협 보고서'),
]

# # Login
# urlpatterns += [
#     path('login/', auth.login_view),
#     path('logout/', auth.logout_view),
# ]

# Dashboard Customize
# urlpatterns +=[
#     path('dashboard/grid/save/', gridstack.save_layout),
#     path('dashboard/grid/load/', gridstack.load_layout),
#     path('dashboard/grid/delete/', gridstack.delete_layout),
#     path('dashboard/grid/layouts/', gridstack.list_layouts),
#     path('dashboard/grid/items/<type>/', gridstack.add_item),
#     path('dashboard/grid/items/', gridstack.list_items),
# ]

# Rule AJAX
# urlpatterns += [
#     # Detail Modal
#     path('rules/<type>/details/', ajax.rule_details),

#     # Edit Modal
#     path('rules/<type>/edit/', ajax.rule_edit_modal),
#     path('custom/edit/', ajax.edit_rule),
#     path('custom/edit/add_rule/', ajax.edit_rule_add_action),
#     path('custom/edit/property/', ajax.edit_add_log_property),

#     # Delete Modal
#     path('custom/delete/', ajax.delete_rule),

#     # Add Modal
#     path('rules/<type>/add/', ajax.rule_add_modal),
#     path('custom/add/<type>/', ajax.add_rule_section),
#     path('custom/add/', ajax.add_rule),

#     # On/Off Action
#     path('rules/<type>/on_off/', ajax.on_off),
# ]

# AJAX
# urlpatterns += [
#     # Topbar alert
#     path("topbar/alert/", ajax.topbar_alert),

#     # Log Management
#     path("modal/log/<type>/", ajax.log_modal),
    
#     # Neo4j Graph Visualization
#     path("neo4j/", aws.detection.neo4j_graph),
    
#     # Dashboard Status AJAX ajax
#     # path("dashboard/status/", dashboard_v0.get_server_status),
    
#     # User Threat AJAX ajax
#     path('visuals/user/details/', ajax.user_details),
# ]

# Integrations
# urlpatterns += [
#     # NCP
#     path("integration/ncp/check/", integrations.integration_NCP),
#     path("integration/ncp/insert/", integrations.insert_NCP),
#     # AWS
#     path("integration/aws/check/", integrations.integration_AWS),
#     path("integration/aws/insert/", integrations.insert_AWS),
#     # AZURE
#     path("integration/azure/check/", integrations.integration_Azure),
#     path("integration/azure/insert/", integrations.insert_Azure),
# ]

# Test
urlpatterns += [
    path('test/', tests.test),
    path('backup/', tests.backup),
    path('test/cyto', tests.cyto),
    path('ajax_src/', tests.ajax_src),
    path('ajax_dst/', tests.ajax_dst),
    path('ajax_js/', tests.ajax_js)
]
