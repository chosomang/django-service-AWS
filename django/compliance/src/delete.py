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
graph = Graph(f"bolt://{host}:7689", auth=(username, password))

def delete(request):
    data = dict(request.POST.items())
    file_name = data['file_name']
    delete_evidence = f"""
    MATCH (n:Compliance:Evidence:File{{name:'{file_name}'}})

    DETACH DELETE n
    """

    file_path = os.path.join(settings.MEDIA_ROOT, 'result', file_name)

    try:
        os.remove(file_path)
        graph.evaluate(delete_evidence)
        response = "증적 파일이 삭제되었습니다."
    except:
        response = 'Error'
    finally:
        return HttpResponse(response)