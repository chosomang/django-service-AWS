from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def asset():

    results = graph.run(f"""
    MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data)-[:ASSET]->(m:Evidence:Compliance:Asset)
    RETURN
        n.name as dataType,
        m.type as assetType,
        m.serial_no as assetNo,
        m.name as assetName,
        m.usage as assetUsage,
        m.data as assetData,
        m.level as assetLevel,
        m.poc as assetPoC,
        m.user as assetUser,
        m.date as assetDate
    ORDER BY
        dataType asc
    """)
    response = []
    for result in results:
        response.append(dict(result.items()))


    data_list = graph.evaluate(f"""
        MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data)
        where n.name <> 'File'
        with n.name as dataType order by dataType asc
        RETURN
            collect(dataType) as dataType
    """)
    
    return {'assets': response, 'data_list': data_list}
