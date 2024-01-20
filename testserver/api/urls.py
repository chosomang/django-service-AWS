from django.urls import path
from api import views

from django.conf import settings
from django.conf.urls.static import static

from .token_views import CustomTokenObtainPairView

urlpatterns = [
    # Dashboard
    path('', views.index),
    path('health/', views.health),
    path('receive-metrics/', views.receive_metrics, name='receive-metrics'),
    path('get_metric_data/<str:instance_id>/', views.get_metric_data, name='get_metric_data'),
    path('get_all_metrics/<str:uuid>/', views.get_all_metrics, name='get_all_metrics'),
    path('get_metrics_by_uuid/<str:uuid>/', views.get_metrics_by_uuid, name='get_metrics_by_uuid'),
    
    # JWT Token
    path('jwt_token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('get_token/', views.create_jwt_token, name='get_token')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)