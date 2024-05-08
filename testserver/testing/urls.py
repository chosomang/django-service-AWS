from django.urls import path
from .src import tests
from .src.finevo import integration, log

urlpatterns = [
    path('', tests.main_test),
    path('ajax/', tests.test_ajax),
    path('dashboard/', tests.dashboard),
    path('trigger/', tests.running_trigger),
    path('trigger/trigger/', tests.trigger, name='trigger'),
    path('cloudformation/', tests.cloudformation, name='cloudformation'),
    path('createIamPolicy/', tests.create_iam_policy, name='createIamPolicy'),
    path('login/', tests.login_, name='login'),
    path('register/', tests.register_, name='register'),
    path('log/<system>/', log.list_logs),
    path('integration/genian/', integration.integration_genian),
]