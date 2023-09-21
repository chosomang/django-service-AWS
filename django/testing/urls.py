from django.urls import path
from .src import tests

urlpatterns = [
    path('', tests.main_test),
    # path('backup/', tests.backup),
    # path('test/cyto', tests.cyto),
    # path('ajax_src/', tests.ajax_src),
    # path('ajax_dst/', tests.ajax_dst),
    # path('ajax_js/', tests.ajax_js)
]