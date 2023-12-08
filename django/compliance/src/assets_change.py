from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def asset(data):
    dataType = data['dataType']
    
    results = graph.run(f"""
    MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data{{name:'{dataType}'}})
    OPTIONAL MATCH (n)-[:ASSET]->(m:Evidence:Compliance:Asset)
    RETURN
        n.name as dataType,
        n.comment as dataComment,
        m.type as assetType,
        m.serial_no as assetNo,
        m.name as assetName,
        m.usage as assetUsage,
        m.data as assetData,
        m.level as assetLevel,
        m.poc as assetPoC,
        m.user as assetUser,
        m.date as assetDate
    """)
    response = []
    for result in results:
        response.append(dict(result.items()))
        

    results = graph.run(f"""
    MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data{{name:'{dataType}'}})
    return
        n.name as dataType,
        n.comment as dataComment
    """)
    data_list = []
    for result in results:
        data_list.append(dict(result.items()))

    return {'assets': response,
            'data_list': data_list}