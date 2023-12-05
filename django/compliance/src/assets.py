from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def view():

    results = graph.run(f"""
    MATCH (c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article)
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

    # results = graph.run(f"""
    # match (d:Data:Law:Compliance)<-[:DATA]-(c:Category:Compliance:Law)-[:EVIDENCE]->(a:Article:Isms_p:Compliance{{art_no:'{art_no}'}})
    # with split(d.file,'.')[1] as file
    # return file
    # """)
    # response2 = []
    # for result in results:
    #     response2.append(dict(result.items()))


    version_list = graph.evaluate(f"""
        MATCH (n:Compliance:Version{{name:'Isms_p'}})       
        return COLLECT(n.date)
    """)
    
    return {'compliance': response, 'version_list': version_list}
