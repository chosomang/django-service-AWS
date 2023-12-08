from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def view(data):

    dataType = data['dataType']

    results = graph.run(f"""
    MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data{{name:'{dataType}'}})
    OPTIONAL MATCH (n)-[:FILE]->(m:Evidence:Compliance:File)
    RETURN
        m.name as fileName,
        m.comment as fileComment,
        m.author as fileAuthor,
        m.poc as filePoC,
        m.version as fileVersion,
        m.upload_date as uploadDate
    """)
    response = []
    for result in results:
        response.append(dict(result.items()))


    return response
