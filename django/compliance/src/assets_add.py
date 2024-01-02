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

def add(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        assetType = data.get('assetType','')
        assetName = data.get('assetName','')
        serialNo = data.get('serialNo','')
        assetUsage = data.get('assetUsage','')
        assetData = data.get('assetData','')
        assetLevel = data.get('assetLevel','')
        assetPoC = data.get('assetPoC','')
        assetUser = data.get('assetUser','')
        dataType = data.get('dataType','')

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or update the node with properties
        add_assets = f"""
        MATCH (a:Compliance:Evidence:Product{{name:'Asset Manage'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{dataType}'}})
        MERGE (n:Compliance:Evidence:Asset{{type:'{assetType}', serial_no:'{serialNo}', name:'{assetName}', usage:'{assetUsage}', data:'{assetData}', level:'{assetLevel}', poc:'{assetPoC}', user:'{assetUser}', date:'{timestamp}'}})
        MERGE (d)-[:ASSET]->(n)
        """
        graph.run(add_assets)

        response = "자산이 업로드 되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return HttpResponse(response)
