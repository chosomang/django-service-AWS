from django.conf import settings
from py2neo import Graph
from datetime import datetime

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def test():
    # test용으로 다 출력해보기
    test_list = graph.evaluate(f"""
    MATCH (n:Isms_p:Compliance)
    RETURN         
        collect(n) AS n,
         collect(id(n)) AS id
    """)

    response={
        'test_string':'test_string',
        'test_list': test_list,
    }

    return response

def add_evidence(dict):
    title=dict['title']

    name=dict['file_name']
    comment=dict['comment']
    version_date=datetime.now()


    cypher= f"""
        MERGE (e:Compliance:Evidence {{
            name:'evidence'
        }})

        MERGE (t:Categoary:Compliance:Evidence {{
            name:'{title}'
        }})

        MERGE (d:Compliance:Data:Evidence {{
            name:'{name}',
            comment:'{comment}',
            version_date:'{version_date}'
        }})

        MERGE (e)-[:CATEGORY]->(t)-[:DATA]->(d)


    """
    graph.evaluate(cypher)

def get_category():
    category_list=graph.evaluate(f"""
        MATCH (c:Category:Compliance:Evidence)
        RETURN COLLECT(c)
    """)

    return category_list

def get_details():
    details_list=graph.evaluate(f"""
        MATCH (c:Category:Compliance:Evidence)-[:DATA]->(f)
        RETURN COLLECT(c), COLLECT(f) AS f
    """)

    return details_list





    



