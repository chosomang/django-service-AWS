# /webAPP/django/dashboard/
# 127.0.0.1/dashboard
from django.urls import path
from dashboard.src.v1 import gridstack_items
from dashboard.src.v1 import gridstack
from dashboard.src.v1 import dashboard
from dashboard import views
from django.conf.urls.static import static

# dashboard/
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
]
# dashboard/grid
urlpatterns += [
    path('grid/save/', gridstack.save_layout),
    path('grid/load/', gridstack.load_layout),
    path('grid/delete/', gridstack.delete_layout),
    path('grid/layouts/', gridstack.list_layouts),
    path('grid/items/<type>/', gridstack.add_item),
    path('grid/items/', gridstack.list_items),
]
# dashboard/status
urlpatterns += [
    path("status/", dashboard.get_server_status),
]
urlpatterns += [
    path('test/', dashboard.test)
]