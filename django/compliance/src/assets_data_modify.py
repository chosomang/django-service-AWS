# Inside your add.py file
from django.shortcuts import HttpResponse
from django.conf import settings
from py2neo import Graph
import os
from datetime import datetime
from ..models import Document

# Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def modify(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        dataType = data.get('dataType','')
        assetData = data.get('assetData','')
        dataComment = data.get('dataComment','')

        modifyData = f"""
        MATCH (a:Compliance:Evidence:Product{{name:'Asset Manage'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{dataType}'}})
        set d.name = '{assetData}', d.comment = '{dataComment}'
        """
        graph.run(modifyData)

        response = "자산 카테고리가 수정되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return HttpResponse(response)
