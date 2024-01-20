# token_api/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserCreateSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    pass
