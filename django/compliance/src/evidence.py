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
        MATCH (:Compliance)-[:COMPLIANCE]->(c:Compliance)
        WHERE c.name <> 'Evidence'
        RETURN c.name
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_compliance_articles(dict):
    compliance = dict['compliance_selected']
    response=[]
    cypher=f"""
        OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(:Version)-[:CHAPTER]->(:Chapter)-[:SECTION]->(:Section)-[:ARTICLE]->(a:Article)
        WITH a
        WHERE a IS NOT NULL
        RETURN a.no AS no, a.name AS name ORDER BY a.no

        UNION

        OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:CHAPTER]->(:Chapter)-[:SECTION]->(:Section)-[:ARTICLE]->(a:Article)
        WITH a
        WHERE a IS NOT NULL
        RETURN a.no AS no, a.name AS name ORDER BY a.no

        UNION

        OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:CHAPTER]->(:Chapter)-[:ARTICLE]->(a:Article)
        WITH a
        WHERE a IS NOT NULL
        RETURN a.no AS no, a.name AS name ORDER BY a.no

        UNION

        OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:ARTICLE]->(a:Article)
        WITH a
        WHERE a IS NOT NULL
        RETURN a.no AS no, a.name AS name ORDER BY a.no
    """

    results = graph.run(cypher)
    for result in results:
        response.append({'no':result['no'], 'name': result['name']})
        
    return response

def get_laws():
    response=[]
    cypher=f"""
        MATCH (c:Compliance:Law)-[:CHAPTER]->(:Chapter:Law)
        RETURN DISTINCT c.name 
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_law_chapters(dict):
    #만약 chapter까지만 있으면 거기까지만, section까지 있으면 section까지
    law = dict['law_selected']
    response=[]
    cypher=f"""
        MATCH (c:Compliance:Law{{name:'{law}'}})-[:CHAPTER]->(ch:Chapter)-[:SECTION]->(s:Section)
        RETURN '['+s.no+'] '+s.name AS s
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def add_data(dict):
    name=dict['name']
    comment=dict['comment']
    author=dict['author']
    last_update=datetime.now()
    compliance=dict['compliance']
    article_selected=dict['article_selected']

    if name == '':
        return 'name NULL'

    #중복 체크 필요
    cypher=f"""
        MATCH (c:Data:Compliance:Evidence{{
            name:'{name}'
        }})
        RETURN count(c)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    #매핑 리스트가 있을 때(컴플라이언스와 관계 생성)
    if  name and compliance and article_selected:   
        cypher= f"""
                MATCH (e:Compliance:Evidence{{name:'Evidence'}})
                MATCH (a:Article{{compliance_name:'{compliance}', no:'{article_selected}'}})
                MERGE (e)-[:DATA]->
                    (d:Data:Compliance:Evidence {{
                    name:'{name}',
                    comment:'{comment}',
                    author:'{author}',
                    last_update:'{last_update}'
                }})-[:EVIDENCE]->(a)
                RETURN COUNT(d)
            """
    #매핑할 애들이 없을 때(그냥 증적 노드만 생성)
    elif name: 
        cypher= f"""
                MATCH (e:Compliance:Evidence{{name:'Evidence'}})
                MERGE (e)-[:DATA]->
                    (d:Data:Compliance:Evidence {{
                    name:'{name}',
                    comment:'{comment}',
                    author:'{author}',
                    last_update:'{last_update}'
                }})
                RETURN COUNT(d)
            """

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'



def del_data(dict):
    name=dict['name']
    if name == '':
        return 'fail'

    #하위 노드가 있을 경우 하위 노드(파일)까지 모두 삭제, 아니면 Data만 삭제
    cypher=f"""
        MATCH (d:Compliance:Evidence:Data{{name:'{name}'}})
        WITH d
        OPTIONAL MATCH (d)-[:DATA]->(f:File:Compliance:Evidence)
        WITH d, COLLECT(f) AS file_list
        FOREACH (f IN file_list| DETACH DELETE f)
        DETACH DELETE d
        RETURN count(d)
    """

    try:
        if graph.evaluate(cypher) >= 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'


def add_file(dict):
    data_name=dict['data_name']
    file_name=dict['file_name']
    comment=dict['comment']
    author=dict['author']
    poc=dict['poc']
    version=dict['version']
    upload_date=datetime.now()

    if file_name=='':
        return 'NULL'

    #중복체크
    cypher=f"""
        MATCH (d:Data:Evidence:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{file_name}'}})
        RETURN count(f)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    cypher= f"""
        MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})
        MERGE (d)-[:FILE]->(f:File:Compliance:Evidence {{
            name:'{file_name}',
            comment:'{comment}',
            author:'{author}',
            poc:'{poc}',
            version:'{version}',
            upload_date:'{upload_date}'
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



def del_file(dict):
    data_name=dict['data_name']
    file_name=dict['file_name']

    cypher= f"""
        MATCH (c:Data:Compliance:Evidence{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence {{name:'{file_name}'}})
        DETACH DELETE f
        RETURN count(f)
    """

    try:
        if 1 == graph.evaluate(cypher):
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'


def get_data(data=None):
    response=[]
    if data==None:
        cypher=f"""
            MATCH (d:Data:Compliance:Evidence)
            RETURN d AS data
        """

        results = graph.run(cypher)
        for result in results:
            response.append(result)
            
    else:
        cypher=f"""
            MATCH (d:Data:Compliance:Evidence)
            WHERE d.name='{data}'
            RETURN d AS data
        """
        results = graph.run(cypher)
        for result in results:
            response.append(result)

    return response

def get_file(data=None):
    if data==None:
        return "잘못된 데이터"
    else:
        data=graph.evaluate(f"""
            MATCH (d:Data:Compliance:Evidence{{name:'{data}'}})-[:FILE]->(file:File:Compliance:Evidence)
            RETURN collect(file)
        """)

    return data


# 컴플라이언스와 증적 파일과 매핑된 애들을 갖고 오기
def get_compliance_list(search_cate=None, search_content=None):
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
            MATCH (ver:Version:Compliance)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
            RETURN ver, chap, sec, arti ORDER BY arti.no
        """

    results = graph.run(cypher)
    for result in results:
     response.append(result)

    return response







    



