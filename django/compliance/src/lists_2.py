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
    article_list = graph.evaluate(f"""
    MATCH (n:Isms_p:Compliance:Article{{no:'{no}'}})
    RETURN COLLECT(n)
    """)

    evidence_list = graph.evaluate(f"""
    MATCH p=(n:Compliance:Evidence:Data)-[:EVIDENCE]->(c:Compliance:Isms_p:Article{{no:'{no}'}})
    RETURN COLLECT(n)
    """)

    response={
        'test_string':'ISMS-P 항목별 관리',
        'article_list': article_list,
        'evidence_list' : evidence_list
    }

    return response
