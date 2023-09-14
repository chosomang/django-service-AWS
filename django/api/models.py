from django.db import models

MAX_CYPHER_SIZE = 9999
MAX_TYPE_SIZE = 50

class Cypher(models.Model):
    index = models.IntegerField()
    cypher_type = models.CharField(max_length=MAX_TYPE_SIZE, default='')
    cypher = models.TextField(max_length=MAX_CYPHER_SIZE, default='')

class ApiCypher(models.Model):
    index = models.IntegerField()
    cypher_type = models.CharField(max_length=MAX_TYPE_SIZE, default='')
    cypher = models.TextField(max_length=MAX_CYPHER_SIZE, default='')