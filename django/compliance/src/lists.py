from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def test():
    # test용으로 다 출력해보기
    section_list = graph.evaluate(f"""
    MATCH (n:Isms_p:Compliance:Section)
    RETURN COLLECT(n)
    """)

    article_list = graph.evaluate(f"""
    MATCH (n:Isms_p:Compliance:Article)
    RETURN COLLECT(n)
    """)

    response={
        'test_string':'ISMS-P 항목별 관리',
        'section_list': section_list,
        'article_list': article_list
    }

    return response
