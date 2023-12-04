from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def version(data):
    ver = data['version']
    results = graph.run(f"""
    MATCH (i:Compliance:Version{{name:'Isms_p', date:date('{ver}')}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article)
    WITH split(m.no, '.') as articleNo, c, n, m
    WITH toInteger(articleNo[0]) AS part1, toInteger(articleNo[1]) AS part2, toInteger(articleNo[2]) AS part3, c, n, m
    RETURN
        c.no as chapterNo,
        c.name as chapterName,
        n.no as sectionNo,
        n.name as sectionName,
        m.no as articleNo,
        m.name as articleName,
        m.comment as articleComment
        ORDER BY part1, part2, part3
    """)
    response = []
    for result in results:
        response.append(dict(result.items()))
    return response
