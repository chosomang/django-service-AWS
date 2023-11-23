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

def add_cate(dict):
    name=dict['name']
    comment=dict['comment']
    mapped_1=dict['mapped_1']

    cypher= f"""
        MATCH (e:Compliance:Evidence{{name:'evidence'}})
        MERGE (e)-[:CATEGORY]->
            (c:Category:Compliance:Evidence {{
            name:'{name}',
            comment:'{comment}',
            mapped_1:'{mapped_1}'
        }})
    """
    graph.evaluate(cypher)

def add_data(dict):
    cate_name=dict['cate_name']
    name=dict['name']
    comment=dict['comment']
    version_date=datetime.now()

    cypher= f"""
        MATCH (c:Category:Compliance:Evidence{{name:'{cate_name}'}})
        MERGE (c)-[:DATA]->(d:Compliance:Data:Evidence {{
            name:'{name}',
            comment:'{comment}',
            version_date:'{version_date}'
        }})
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

def get_law_list(evidence_cate=None):
    '''
        MATCH (l:Law:Compliance)-[:CHAPTER]->(c:Chapter:Law:Compliance)-[:SECTION]->(s:Section)-[:MAPPED]->(a:Article:Compliance:Isms_p)<-[:EVIDENCE]-(e:Evidence:Category)
        WHERE e.name='{evidence_cate}'
        RETURN l AS law, c AS chapter, a AS article, s AS section
    '''
    response=[]
    
    cypher=f"""
        MATCH (com:Compliance)-[:VERSION]->(v:Version)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a:Article)<-[:EVIDENCE]-(e:Evidence)
        WHERE e.name="{evidence_cate}"
        RETURN com, v, c, s, a, e
    """
    results = graph.run(cypher)
    for result in results:
     response.append(result)

    return response







    



