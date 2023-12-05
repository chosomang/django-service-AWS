from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def version():

    results = graph.run(f"""
    MATCH (i:Compliance:Version{{name:'Isms_p', date:date('2023-10-31')}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article)
    OPTIONAL MATCH (m)<-[r:COMPLY]-(p:Product:Evidence:Compliance{{name:'AWS'}})
    WITH split(m.no, '.') as articleNo, c, n, m, coalesce(r, {{score: 0}}) as r, p
    WITH toInteger(articleNo[0]) AS part1, toInteger(articleNo[1]) AS part2, toInteger(articleNo[2]) AS part3, c, n, m, r, p
    RETURN
        c.no as chapterNo,
        c.name as chapterName,
        n.no as sectionNo,
        n.name as sectionName,
        m.no as articleNo,
        m.name as articleName,
        m.comment as articleComment,
        r.score as complyScore
    ORDER BY part1, part2, part3
    """)
    response = []
    for result in results:
        response.append(dict(result.items()))


    version_list = graph.evaluate(f"""
        MATCH (n:Compliance:Version{{name:'Isms_p'}})       
        return COLLECT(n.date)
    """)

    results = graph.run(f"""
    MATCH (e:Evidence:Compliance{{name:'Evidence'}})-[:PRODUCT]->(p:Evidence:Compliance:Product)
    RETURN
        p.name as productName
        order by productName
    """)
    product_list = []
    for result in results:
        product_list.append(dict(result.items()))
    
    return {'compliance': response,
            'version_list': version_list,
            'product_list': product_list}
