# Inside your add.py file
from django.shortcuts import HttpResponse
from django.conf import settings
from py2neo import Graph
import os
from datetime import datetime  # Add this import for timestamp

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
        art_no = data['art_no']
        categoryName = data.get('categoryName', '')
        name = data.get('name', '')
        comment = data.get('comment', '')

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or update the node with properties
        add_evidence = f"""
        MATCH (a:Compliance:Isms_p:Article{{no:'{art_no}'}})
        MATCH (c:Evidence:Compliance{{name:'evidence'}})
        MERGE (n:Compliance:Evidence:Category{{name:'{categoryName}'}})
        MERGE (e:Compliance:Evidence:Data{{name:'{name}', comment:'{comment}', version_date:'{timestamp}'}})
        MERGE (c)-[:CATEGORY]->(n)
        MERGE (a)<-[:EVIDENCE]-(n)-[:DATA]->(e)
        """
        graph.run(add_evidence)

        response = "증적 파일이 업로드 되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return HttpResponse(response)
