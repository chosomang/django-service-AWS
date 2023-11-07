from django.urls import path
from . import views

urlpatterns = [
    # Integration
    path('', views.integration_view),
    path('<equipment>/', views.integration_page),
    path("<equipment>/check/", views.integration_check_ajax),
    path("<equipment>/insert/", views.integration_insert_ajax),
    path("<equipment>/collection/", views.integration_collection_ajax),
]
