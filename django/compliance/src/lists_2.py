from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7689", auth=(username, password))

def test(data):
    no = data['no']

    results  = graph.run(f"""
    OPTIONAL MATCH (l:Law)-[:VERSION]->(v:Version)-[*]->(a:Article)<-[:MAPPED]->(i:Certification{{no:'{no}'}})
    WITH l, v, a, i
    OPTIONAL MATCH (v)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a)<-[:MAPPED]->(i)
    WITH l, v, c, a, i, s
    OPTIONAL MATCH (v)-[:CHAPTER]->(c1:Chapter)-[:ARTICLE]->(a)<-[:MAPPED]->(i)
    RETURN
    COALESCE(l.name, '') AS lawName,
    COALESCE(COALESCE(c.no + '장', '') + COALESCE(c1.no + '장', ''), '') AS chapterNo,
    COALESCE(COALESCE(c.name, '') + COALESCE(c1.name, ''), '') AS chapterName,
    COALESCE(s.no + '절', '') AS sectionNo,
    COALESCE(s.name, '') AS sectionName,
    COALESCE(a.no + '조', '') AS articleNo,
    COALESCE(a.name, '') AS articleName
    ORDER BY lawName
    """)
    law = []
    for result in results:
        law.append(dict(result.items()))
    
    # query 수정 완
    results = graph.run(f"""
    MATCH (n:Certification:Compliance:Article{{compliance_name:'Isms_p', no:'{no}'}})
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

    #query 수정 완 
    results = graph.run(f"""
    MATCH (f:File:Compliance:Evidence)<-[:FILE]-(d:Compliance:Evidence:Data)-[:EVIDENCE]->(a:Compliance:Certification:Article{{compliance_name:'Isms_p', no:'{no}'}})
    RETURN
        f.name as fileName,
        f.comment as fileComment,
        f.version as fileVersion,
        f.file as dataFile,
        f.last_update as fileLastUpdate,
        f.upload_date as fileUploadDate,
        f.poc as filePoc,
        f.author as fileAuthor,
        d.name as dataName,
        d.comment as dataComment
    """)
    evidence = []
    for result in results:
        evidence.append(dict(result.items()))

    results = graph.run(f"""
    MATCH (c:Compliance:Evidence:Data)-[:EVIDENCE]->(a:Compliance:Certification:Article{{compliance_name:'Isms_p', no:'{no}'}})
    RETURN
        c.name as dataName,
        c.comment as dataComment,
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
