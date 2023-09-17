from M_equipments import views
from M_equipments.src import module
from django.urls import path

urlpatterns = [
    path('', views.integration_view),
    path('<type>/', views.integration_type),
]
# Integrations
urlpatterns += [
    # NCP
    path("ncp/check/", module.integration_NCP),
    path("ncp/insert/", module.insert_NCP),
    # AWS
    path("aws/check/", module.integration_AWS),
    path("aws/insert/", module.insert_AWS),
    # AZURE
    path("azure/check/", module.integration_Azure),
    path("azure/insert/", module.insert_Azure),
]