from django.urls import path
from .src import tests

urlpatterns = [
    path('', tests.main_test),
    path('test2/', tests.test2)
]