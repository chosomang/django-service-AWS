from django.urls import include, path
from configurations import views

# path:
#   ./configurations/
urlpatterns = [
    path('<config_type>', views.configuration_view)
]
