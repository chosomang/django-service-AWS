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
    pro = data['product']

    results = graph.run(f"""
    MATCH (i:Compliance:Version{{name:'Isms_p', date:date('{ver}')}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article)
    OPTIONAL MATCH (m)<-[r:COMPLY]-(p:Product:Evidence:Compliance{{name:'{pro}'}})
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

    return response


def comply(data):
    version = data['version']
    product = data['product']
    article = data['article']
    score = data['value']

    #try 넣어야됨
    if score  == '0':

        results = graph.evaluate(f"""
        MATCH (i:Compliance:Version{{name:'Isms_p', date:date('{version}')}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article{{no:'{article}'}})<-[r:COMPLY]-(p:Product:Evidence:Compliance{{name:'{product}'}})
        detach delete r
        return 0 as score
        """)

    else:
        if 2 >= graph.evaluate(f"""
        MATCH (i:Compliance:Version{{name:'Isms_p', date:date('{version}')}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article{{no:'{article}'}})
        OPTIONAL MATCH (m)<-[r:COMPLY]-(p:Product:Evidence:Compliance{{name:'{product}'}})
        with i, m, p, r
        call apoc.do.when (r is null,
        'match (pro:Product:Evidence:Compliance{{name:"{product}"}}) merge (m)<-[re:COMPLY{{score:{score}}}]-(pro) return re.score as score',
        'set r.score = {score} return r.score as score',
        {{r:r, p:p, m:m, i:i}})
        yield value
        return value.score as score
        """) >= 1 :
            return "성공"
        else:
            return "실패"