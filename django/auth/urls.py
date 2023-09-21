from auth import login
from django.urls import path


urlpatterns = [
    path('login/', login.login_view, name='login'),
    path('logout/', login.logout_view, name='logout'),
]
