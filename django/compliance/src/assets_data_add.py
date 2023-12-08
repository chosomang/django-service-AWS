# Inside your add.py file
from django.shortcuts import HttpResponse
from django.conf import settings
from py2neo import Graph
import os
from datetime import datetime  # Add this import for timestamp
from ..models import Document

# Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def add(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        dataName = data.get('assetData', '')
        dataComment = data.get('dataComment', '')
        print(data)

        # Create or update the node with properties
        add_assets_data = f"""
        MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})
        MERGE (n:Compliance:Evidence:Data{{name:'{dataName}', comment:'{dataComment}'}})
        MERGE (c)-[:DATA]->(n)
        """
        graph.run(add_assets_data)

        response = "자산 데이터가 업로드 되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return HttpResponse(response)
