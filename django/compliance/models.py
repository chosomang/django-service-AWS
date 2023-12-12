from django.db import models
import os

class Document(models.Model):
    title = models.CharField(max_length=200)
    uploadedFile = models.FileField(upload_to="result/")
    dateTimeOfUpload = models.DateTimeField(auto_now=True)
