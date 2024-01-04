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
        art_no = data['art_no']
        dataName = data.get('dataName', '')
        dataComment = data.get('dataComment', '')
        fileComment = data.get('fileComment', '')
        author = data.get('author', '')
        poc = data.get('poc', '')
        version = data.get('version', '')
        uploadedFile = request.FILES["uploadedFile"]

        # 디비에 파일 정보 저장
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
        MATCH (a:Compliance:Certification:Article{{compliance_name:'Isms_p', no:'{art_no}'}})
        MATCH (c:Evidence:Compliance{{name:'Evidence'}})
        MERGE (n:Compliance:Evidence:Data{{name:'{dataName}', comment:'{dataComment}'}})
        MERGE (e:Compliance:Evidence:File{{name:'{uploadedFile.name}', comment:'{fileComment}', upload_date:'{timestamp}', version:'{version}', author:'{author}', poc:'{poc}'}})
        MERGE (c)-[:DATA]->(n)
        MERGE (a)<-[:EVIDENCE]-(n)
        merge (n)-[:FILE]->(e)
        """
        graph.run(add_evidence)

        response = "증적 파일이 업로드 되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return HttpResponse(response)
