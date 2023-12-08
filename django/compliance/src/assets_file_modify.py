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
        fileName = data.get('fileName','')
        fileComment = data.get('fileComment','')
        fileAuthor = data.get('fileAuthor','')
        fileVersion = data.get('fileVersion','')
        filePoC = data.get('filePoC','')

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or update the node with properties
        add_assets = f"""
        MATCH (a:Compliance:Evidence:Product{{name:'Asset Manage'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'File'}})-[:FILE]->(n:Compliance:Evidence:File{{name:'{fileName}'}})
        SET
            n.comment = '{fileComment}',
            n.author = '{fileAuthor}',
            n.version = '{fileVersion}',
            n.poc = '{filePoC}',
            n.last_update = '{timestamp}'
        """
        graph.run(add_assets)

        response = "자산이 수정 되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return HttpResponse(response)
