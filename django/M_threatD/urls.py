from django.urls import include, path
from M_threatD import views
from M_threatD import modals

urlpatterns = [
    ## alert
    path('alert/<cloud>/', views.alert_view),
    ## rules
    path('rules/<cloud>/', views.rules_view),
    ## visuals
    path('visuals/<cloud>/', views.visuals_view),
    # Detail Modal
    path('rules/<cloud>/details/', modals.rule_details),
    # Edit Modal
    path('rules/<cloud>/edit/', modals.rule_edit_modal)
]
