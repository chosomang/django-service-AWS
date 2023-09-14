from django.urls import path, include
from rest_framework import routers
from api import views
from .views import create_cypher
from .views import CypherListCreateView
from .views import CypherViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'cypher', CypherViewSet)

urlpatterns = [
    # Dashboard
    path('', views.index),
    path('create/', create_cypher, name='create_cypher'),
    path('', include(router.urls)) # /cypher/{}
    # path('create/', CypherListCreateView.as_view(), name='cypher_create')
]