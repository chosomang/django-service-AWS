from django.urls import include, path
from M_threatD import views

urlpatterns = [
    ## alert
    path('alert/<cloud_type>/', views.alert_view),
    ## rules
    path('rules/<cloud_type>/', views.rules_view),
    ## visuals
    path('visuals/<cloud_type>/', views.visuals_view),
]
