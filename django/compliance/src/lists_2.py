from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def test(data):
    no = data['no']

    results = graph.run(f"""
    MATCH (l:Law)-[:CHAPTER]->(c:Chapter)-[*]->(i:Isms_p{{no:'{no}'}})
    OPTIONAL MATCH (c:Chapter)-[relation]->(element)<-[MAPPED]->(i:Isms_p{{no:'{no}'}})
    WITH
        l.name as lawName,
        c.name as chapterName,
        c.no as chapterNo,
        COLLECT(DISTINCT
            CASE
                WHEN element:Section and relation:SECTION THEN {{ name: element.name, no: element.no + '조' }}
                WHEN element is null and relation is null THEN {{ name: '-', no: '-' }}
                ELSE {{ name: element.name, no: element.no }}
            END
        ) as sections
    UNWIND sections as section
    RETURN DISTINCT
        lawName,
        chapterName,
        chapterNo,
        section.no as sectionNo,
        section.name as sectionName
    """)
    law = []
    for result in results:
        law.append(dict(result.items()))
    
    results = graph.run(f"""
    MATCH (n:Isms_p:Compliance:Article{{no:'{no}'}})
    RETURN
        n.no as articleNo,
        n.name as articleName,
        n.comment as articleComment,
        n.checklist as articleChecklist,
        n.example as articleExample
    """)
    article = []
    for result in results:
        article.append(dict(result.items()))

    results = graph.run(f"""
    MATCH (d:Data:Compliance:Evidence)<-[:DATA]-(c:Compliance:Evidence:Category)-[:EVIDENCE]->(a:Compliance:Isms_p:Article{{no:'{no}'}})
    RETURN
        d.name as dataName,
        d.comment as dataComment,
        d.version_date as dataVersion,
        d.file as dataFile,
        c.name as categoryName,
        c.comment as categoryComment
    """)
    evidence = []
    for result in results:
        evidence.append(dict(result.items()))

    results = graph.run(f"""
    MATCH (c:Compliance:Evidence:Category)-[:EVIDENCE]->(a:Compliance:Isms_p:Article{{no:'{no}'}})
    RETURN
        c.name as categoryName,
        c.comment as categoryComment,
        a.no as art_no
    """)
    category = []
    for result in results:
        category.append(dict(result.items()))
    
    return {'law': law,
            'article_list': article,
            'evidence_list' : evidence,
            'category' : category
    }
