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
    category_name=dict['category_name']
    category_comment=dict['category_comment']
    category_mapped_1=dict['category_mapped_1']
    #category_mapped_ismsp=mapped_ismsp

    data_name=dict['data_name']
    data_comment=dict['data_comment']
    data_version_date=datetime.now()


    cypher= f"""
        MERGE (e:Compliance:Evidence {{
            name:'evidence'
        }})

        MERGE (t:Category:Compliance:Evidence {{
            name:'{category_name}',
            comment:'{category_comment}',
            mapped_1:['{category_mapped_1}'],
        }})

        MERGE (d:Compliance:Data:Evidence {{
            name:'{data_name}',
            comment:'{data_comment}',
            version_date:'{data_version_date}'
        }})

        MERGE (e)-[:CATEGORY]->(t)-[:DATA]->(d)
    """
    graph.evaluate(cypher)

def get_category(category=None):
    if category==None:
        response=graph.evaluate(f"""
            MATCH (c:Category:Compliance:Evidence)
            RETURN COLLECT(c)
        """)
    else:
        response=graph.evaluate(f"""
            MATCH (c:Category:Compliance:Evidence)
            WHERE c.name='{category}'
            RETURN COLLECT(c)
        """)
    return response

def get_data(category=None):
    if category==None:
        return "잘못된 데이터"
    else:
        data=graph.evaluate(f"""
            MATCH (c:Category:Compliance:Evidence)-[:DATA]->(d:Compliance:Data:Evidence)
            WHERE c.name='{category}'
            RETURN COLLECT(d)
        """)

    return data

def get_law_list():
    law_list=graph.evaluate(f"""
            MATCH 
                (i:Isms_p:Compliance:Version)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a:Article)
            RETURN DISTINCT COLLECT(i)
        """)

    return law_list

def get_chapter_list():
    chapter_list=graph.evaluate(f"""
            MATCH 
                (i:Isms_p:Compliance:Version)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a:Article)
            RETURN COLLECT(c)
        """)

    return chapter_list

def get_section_list():
    section_list=graph.evaluate(f"""
            MATCH 
                (i:Isms_p:Compliance:Version)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a:Article)
            RETURN COLLECT(s)
        """)

    return section_list

def get_article_list():
    article_list=graph.evaluate(f"""
            MATCH 
                (i:Isms_p:Compliance:Version)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a:Article)
            WITH a
            ORDER BY a.no
            RETURN COLLECT(a)
        """)

    return article_list








    



