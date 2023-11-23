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
    if name == '':
        return 'fail'
    comment=dict['comment']

    cypher= f"""
        MATCH (e:Compliance:Evidence{{name:'evidence'}})
        MERGE (e)-[:CATEGORY]->
            (c:Category:Compliance:Evidence {{
            name:'{name}',
            comment:'{comment}'
        }})
        RETURN COUNT(c)
    """
    try:
        if 1 == graph.evaluate(cypher):
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'

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
    response=[]
    if category==None:
        cypher=f"""
            MATCH (c:Category:Compliance:Evidence)
            RETURN c AS cate
        """

        results = graph.run(cypher)
        for result in results:
            response.append(result)
            
    else:
        cypher=f"""
            MATCH (c:Category:Compliance:Evidence)
            WHERE c.name='{category}'
            RETURN c AS cate
        """
        results = graph.run(cypher)
        for result in results:
            response.append(result)

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


def get_law_list(search_cate=None, search_content=None):
    '''
        MATCH (l:Law:Compliance)-[:CHAPTER]->(c:Chapter:Law:Compliance)-[:SECTION]->(s:Section)-[:MAPPED]->(a:Article:Compliance:Isms_p)<-[:EVIDENCE]-(e:Evidence:Category)
        WHERE e.name='{evidence_cate}'
        RETURN l AS law, c AS chapter, a AS article, s AS section
    '''
    response=[]
    
    if search_cate=="com":
        cypher=f"""
            MATCH (com:Compliance)-[:VERSION]->(ver:Version)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)
            WHERE {search_cate}.name="{search_content}"
            RETURN com, ver, chap, sec, arti ORDER BY arti.no
        """
    elif search_cate=="evi":
        cypher=f"""
            MATCH (com:Compliance)-[:VERSION]->(ver:Version)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Evidence)
            WHERE {search_cate}.name="{search_content}"
            RETURN com, ver, chap, sec, arti ORDER BY arti.no
        """

    results = graph.run(cypher)
    for result in results:
     response.append(result)

    return response







    



