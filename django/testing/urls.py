from django.urls import path
from .src import tests

urlpatterns = [
    path('', tests.main_test),
    path('design/', tests.design_test),
    path('dashboard/', tests.dashboard),
    path('trigger/', tests.running_trigger),
    path('trigger/trigger/', tests.trigger, name='trigger')
]