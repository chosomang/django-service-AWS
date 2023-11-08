from django.urls import path
from .src import tests

urlpatterns = [
    path('', tests.main_test),
    path('test2/', tests.test2),
    path('trigger/', tests.running_trigger),
    path('trigger/trigger/', tests.trigger, name='trigger')
]