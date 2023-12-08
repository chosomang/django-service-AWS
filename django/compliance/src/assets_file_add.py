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
        fileComment = data.get('fileComment', '')
        author = data.get('author', '')
        poc = data.get('poc', '')
        version = data.get('version', '')
        uploadedFile = request.FILES["uploadedFile"]
        # Saving the information in the database
        document = Document(
            title=fileComment,
            uploadedFile=uploadedFile
        )
        document.save()

        documents = Document.objects.all()

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uploadedFile.name = uploadedFile.name.replace(' ', '_')

        # Create or update the node with properties
        add_evidence = f"""
        MATCH (p:Product:Compliance:Evidence{{name:'Asset Manage'}})-[:DATA]->(a:Compliance:Evidence:Data{{name:'File'}})
        MERGE (e:Compliance:Evidence:File{{name:'{uploadedFile.name}', comment:'{fileComment}', upload_date:'{timestamp}', version:'{version}', author:'{author}', poc:'{poc}'}})
        merge (a)-[:FILE]->(e)
        """
        graph.run(add_evidence)

        response = "증적 파일이 업로드 되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return HttpResponse(response)
