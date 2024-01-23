from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=str(uuid.uuid4()), unique=True)
    email = models.EmailField(unique=True)  # 이메일 필드 추가
    db_name = models.CharField(max_length=50, default=False, unique=True)
    is_active = models.BooleanField(default=False)