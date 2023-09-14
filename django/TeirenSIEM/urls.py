
from django.urls import path
from TeirenSIEM import views
from TeirenSIEM import setting, test, ajax, integration, dashboard, risk


# Views
urlpatterns = [
    # Dashboard
    path('', views.dashboard_view),
    path('dashboard/', views.dashboard_view),

    # Log Management
    path('log/<type>/', views.log_view),

    # Integration
    path('integration/', views.integration_view),
    path('integration/<type>/', views.integration_type),

    # Risk Management
    ## alert
    path('alert/<type>/', views.alert_view),
    ## rules
    path('rules/<type>/', views.rules_view),
    ## visuals
    path('visuals/<type>/', views.visuals_view),

    # Settings
    path('settings/<type>/', views.settings_view),

    # Compliance
    path('compliance/compliance/', views.compliance_view),
    path('compliance/report/', views.report_view),
    path('compliance/report_month/', views.report_month_view, name='[Teiren] 월간 위협 보고서'),
]

# Login
urlpatterns += [
    path('login/', setting.login.login.login_view),
    path('logout/', setting.login.login.logout_view),
]

# Dashboard Customize
urlpatterns +=[
    path('dashboard/grid/save/', dashboard.gridstack.save_layout),
    path('dashboard/grid/load/', dashboard.gridstack.load_layout),
    path('dashboard/grid/delete/', dashboard.gridstack.delete_layout),
    path('dashboard/grid/layouts/', dashboard.gridstack.list_layouts),
    path('dashboard/grid/items/<type>/', dashboard.gridstack.add_item),
    path('dashboard/grid/items/', dashboard.gridstack.list_items),
]

# Rule AJAX
urlpatterns += [
    # Detail Modal
    path('rules/<type>/details/', ajax.rule_details),

    # Edit Modal
    path('rules/<type>/edit/', ajax.rule_edit_modal),
    path('custom/edit/', ajax.edit_rule),
    path('custom/edit/add_rule/', ajax.edit_rule_add_action),
    path('custom/edit/property/', ajax.edit_add_log_property),

    # Delete Modal
    path('custom/delete/', ajax.delete_rule),

    # Add Modal
    path('rules/<type>/add/', ajax.rule_add_modal),
    path('custom/add/<type>/', ajax.add_rule_section),
    path('custom/add/', ajax.add_rule),

    # On/Off Action
    path('rules/<type>/on_off/', ajax.on_off),
]

# Alert AJAX
urlpatterns += [
    # Neo4j Graph Visualization
    path("neo4j/", risk.alert.detection.neo4j_graph),

]
# AJAX
urlpatterns += [
    # Topbar alert
    path("topbar/alert/", ajax.topbar_alert),

    # Log Management
    path("modal/log/<type>/", ajax.log_modal),
    
    # Dashboard Status AJAX ajax
    path("dashboard/status/", dashboard.dashboard.get_server_status),
    
    # User Threat AJAX ajax
    path('visuals/user/details/', ajax.user_details),
]

# Integrations
urlpatterns += [
    # NCP
    path("integration/ncp/check/", integration.integrations.integration_NCP),
    path("integration/ncp/insert/", integration.integrations.insert_NCP),
    # AWS
    path("integration/aws/check/", integration.integrations.integration_AWS),
    path("integration/aws/insert/", integration.integrations.insert_AWS),
    # AZURE
    path("integration/azure/check/", integration.integrations.integration_Azure),
    path("integration/azure/insert/", integration.integrations.insert_Azure),
]

# Test
urlpatterns += [
    path('test/', test.tests.test),
    path('backup/', test.tests.backup),
    path('test/cyto', test.tests.cyto),
    path('ajax_src/', test.tests.ajax_src),
    path('ajax_dst/', test.tests.ajax_dst),
    path('ajax_js/', test.tests.ajax_js)
]
