from django.conf import settings
from py2neo import Graph
from datetime import datetime

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def get_compliance():
    response=[]
    cypher=f"""
        MATCH (c:Compliance)
        WHERE c.country IS NOT NULL
        RETURN c.name AS comp
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_compliance_articles(dict):
    compliance = dict['compliance_selected']
    response=[]
    cypher=f"""
        MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(:Version)-[:CHAPTER]->(:Chapter)-[:SECTION]->(:Section)-[:ARTICLE]->(a:Article)
        WHERE c.country IS NOT NULL
        RETURN '['+a.no+'] '+a.name AS a
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def add_cate(dict):
    name=dict['name']
    comment=dict['comment']

    if name == '':
        return 'NULL'

    cypher=f"""
        MATCH (c:Category:Compliance:Evidence{{
            name:'{name}'
        }})
        RETURN count(c)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

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
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'

def mod_date(dict):
    name=dict['name']


def del_cate(dict):
    name=dict['name']
    if name == '':
        return 'fail'

    cypher=f"""
        MATCH (e:Compliance:Evidence:Category{{name:'{name}'}})-[:DATA]->(d:Data:Compliance:Evidence)
        RETURN count(d)
    """
    if graph.evaluate(cypher) == 0:
        cypher=f"""
            MATCH (e:Compliance:Evidence:Category{{name:'{name}'}})
            DETACH DELETE (e)
            RETURN count(e)
        """
    else:
        #하위 노드(증적 파일들)까지 모두 삭제 해버림
        cypher=f"""
            MATCH (e:Compliance:Evidence:Category{{name:'{name}'}})-[:DATA]->(d:Data:Compliance:Evidence)
            DETACH DELETE (e),(d)
            RETURN count(e)
        """

    try:
        if graph.evaluate(cypher) >= 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'


def add_data(dict):
    cate=dict['cate']
    name=dict['name']
    comment=dict['comment']
    author=dict['author']
    version_date=datetime.now()

    if name=='':
        return 'NULL'

    cypher=f"""
        MATCH (c:Category:Compliance{{name:'{cate}'}})-[:DATA]->(d:Data:Evidence:Compliance{{name:'{name}'}})
        RETURN count(d)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    cypher= f"""
        MATCH (c:Category:Compliance:Evidence{{name:'{cate}'}})
        MERGE (c)-[:DATA]->(d:Compliance:Data:Evidence {{
            name:'{name}',
            comment:'{comment}',
            version_date:'{version_date}',
            author:'{author}'
        }})
        RETURN count(d)
    """
    graph.evaluate(cypher)

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'

def del_data(dict):
    cate=dict['cate']
    name=dict['name']

    cypher= f"""
        MATCH (c:Category:Compliance:Evidence{{name:'{cate}'}})-[:DATA]->(d:Compliance:Data:Evidence {{name:'{name}'}})
        DETACH DELETE d
        RETURN count(d)
    """

    try:
        if 1 == graph.evaluate(cypher):
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'

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







    



