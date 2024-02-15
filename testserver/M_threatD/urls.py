from django.urls import path
from . import ajax_views, views

urlpatterns = [
    # Risk Management
    ## alert
    path('notifications/<threat>/', views.notification_view),
    # ## rules
    path('rules/<resourceType>/<logType>/', views.rules_view),
    ## visuals
    path('visuals/<threat>/', views.visuals_view),
    # User Threat AJAX ajax
    path('visuals/user/details/', views.user_details),

    path("neo4j/",views.neo4j_graph),
    
    # Detail Modal
    path('rules/<resourceType>/<logType>/<ruleType>/details/', ajax_views.rule_details),

    # Edit Modal
    path('rules/<resourceType>/<logType>/edit/', ajax_views.rule_edit_modal),
    path('custom/edit/', ajax_views.edit_rule),

    # Delete Modal
    path('custom/delete/', ajax_views.delete_rule),

    # Add Modal
    path('rules/<resourceType>/<logType>/add/', ajax_views.rule_add_modal),
    path('custom/add/<section>/', ajax_views.add_rule_section),
    path('custom/add/', ajax_views.add_rule),

    # On/Off Action
    path('rules/<resourceType>/<logType>/on_off/', ajax_views.on_off)
]
