from django.shortcuts import HttpResponse
from django.conf import settings
from py2neo import Graph
import json
import os

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def delete(data):

    dataType = data.POST['dataType']
    
    delete_assets_data = f"""
    MATCH (p:Compliance:Product:Evidence{{name:'Asset Manage'}})-[:DATA]->(n:Compliance:Evidence:Data{{name:'{dataType}'}})
    OPTIONAL MATCH (n)-[:ASSET]->(a:Compliance:Evidence:Asset)

    DETACH DELETE n, a
    """

    try:
        graph.evaluate(delete_assets_data)
        response = "자산이 삭제되었습니다."
    except:
        response = 'Error'
    finally:
        return HttpResponse(response)