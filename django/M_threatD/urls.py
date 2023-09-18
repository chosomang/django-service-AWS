from django.urls import include, path
from M_threatD import views
from M_threatD import modals

urlpatterns = [
    ## alert
    path('alert/<cloud_type>/', views.alert_view),
    ## rules
    path('rules/<cloud_type>/', views.rules_view),
    ## visuals
    path('visuals/<cloud_type>/', views.visuals_view),
    # Detail Modal
    path('rules/<rule_type>/details/', modals.rule_details),
    # Edit Modal
    path('rules/<rule_type>/edit/', modals.rule_edit_modal)
]
