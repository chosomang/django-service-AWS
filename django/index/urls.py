from auth import login
from index import views
from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index)
]
urlpatterns += [
    path('login/', login.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
