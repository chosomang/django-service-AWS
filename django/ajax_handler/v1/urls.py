from django.urls import path
from ajax_handler.v1.src import ajax_endpoint
from ajax_handler.v1.src import modals_endpoint
from common.risk.v1.notification.detection import neo4j_graph

### modal ###
urlpatterns = [
    # Detail
    path('rules/<rule_type>/details/', modals_endpoint.rule_details),

    # Edit
    path('rules/<cloud_type>/edit/', modals_endpoint.rule_edit_modal),
    path('custom/edit/', modals_endpoint.edit_rule),
    path('custom/edit/add_rule/', modals_endpoint.edit_rule_add_action),
    path('custom/edit/property/', modals_endpoint.edit_add_log_property),

    # Delete
    path('custom/delete/', modals_endpoint.delete_rule),

    # Add
    path('rules/<cloud_type>/add/', modals_endpoint.rule_add_modal),
    path('custom/add/<rule_type>/', modals_endpoint.add_rule_section),
    # path('custom/add/', modals_endpoint.add_rule), # no attribute 'add_rule'

    # On/Off Action
    path('rules/<cloud_type>/on_off/', modals_endpoint.on_off),
]

### ajax ###
urlpatterns += [
    # Topbar alert
    path("topbar/alert/", ajax_endpoint.topbar_alert),

    # Log Management
    path("modal/log/<modal_type>/", ajax_endpoint.log_modal),
    
    # Neo4j Graph Visualization
    path("neo4j/", neo4j_graph),
    
    # Dashboard Status AJAX ajax
    # path("dashboard/status/", dashboard_v0.get_server_status),
    
    # User Threat AJAX ajax
    path('visuals/user/details/', ajax_endpoint.user_details),
]