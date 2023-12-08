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

    serial_no = data.POST['serial_no']

    delete_assets = f"""
    MATCH (n:Compliance:Evidence:Asset{{serial_no:'{serial_no}'}})

    DETACH DELETE n
    """

    try:
        graph.evaluate(delete_assets)
        response = "증적 파일이 삭제되었습니다."
    except:
        response = 'Error'
    finally:
        return HttpResponse(response)