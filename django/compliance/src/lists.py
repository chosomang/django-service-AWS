from django.conf import settings
from py2neo import Graph
# import json

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def test():
    # test용으로 다 출력해보기
    test_list = graph.evaluate(f"""
    MATCH (n:Isms_p:Compliance)
    RETURN COLLECT(n)
    """)

    response={
        'test_string':'그냥 문자열입니다',
        'test_list': test_list
    }

    return response
