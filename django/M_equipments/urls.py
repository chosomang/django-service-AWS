from django.urls import path
from . import views

urlpatterns = [
    # Integration
    path('<pageType>/', views.integration_view),
    path('<equipment>/<logType>/', views.registration_page),
    path("<equipment>/<logType>/check/", views.integration_check_ajax),
    path("<equipment>/<logType>/insert/", views.integration_insert_ajax),
    path("<equipment>/<logType>/collection/", views.integration_collection_ajax),
    path('configuration/delete/<actionType>/', views.integration_delete_ajax),
    path('configuration/trigger/<actionType>/', views.integration_trigger_ajax),
]
