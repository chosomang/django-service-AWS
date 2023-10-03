from django.urls import path
from . import views, rule_ajax
from .src.notification import detection

urlpatterns = [
    # Risk Management
    ## alert
    path('notifications/<threat>/', views.notification_view),
    # ## rules
    path('rules/<cloud>/', views.rules_view),
    ## visuals
    path('visuals/<threat>/', views.visuals_view),

    path("neo4j/",detection.neo4j_graph),
]

urlpatterns +=[
    # Detail Modal
    path('rules/<ruleType>/details/', rule_ajax.rule_details),

    # Edit Modal
    path('rules/<cloud>/edit/', rule_ajax.rule_edit_modal),
    path('custom/edit/', rule_ajax.edit_rule),

    # Delete Modal
    path('custom/delete/', rule_ajax.delete_rule),

    # Add Modal
    path('rules/<cloud>/add/', rule_ajax.rule_add_modal),
    path('custom/add/<section>/', rule_ajax.add_rule_section),
    path('custom/add/', rule_ajax.add_rule),

    # On/Off Action
    path('rules/<cloud>/on_off/', rule_ajax.on_off),
]
