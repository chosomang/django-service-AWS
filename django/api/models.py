from django.db import models

MAX_CYPHER_SIZE = 9999

class Cypher(models.Model):
    index = models.IntegerField()
    cypher = models.TextField(max_length=MAX_CYPHER_SIZE)

class ApiCypher(models.Model):
    index = models.IntegerField()
    cypher = models.TextField(max_length=MAX_CYPHER_SIZE)