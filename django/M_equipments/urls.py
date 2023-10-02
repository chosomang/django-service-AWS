from M_equipments import views
from M_equipments.src import module
from django.urls import path

urlpatterns = [
    path('', views.integration_view),
    path('<equipment>/', views.integration_type),
]

# Integrations
urlpatterns += [
    # AWS
    path("aws/check/", module.integration_AWS),
    path("aws/insert/", module.insert_AWS),
]