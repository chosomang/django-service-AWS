from django.conf import settings
from py2neo import Graph
from datetime import datetime

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

# 전체 컴플라이언스 리스트 가져오기 (Evidence 노드 제외)
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

def get_version(dict):
    compliance = dict['compliance_selected']

    response=[]

    if compliance and compliance!='none':
        cypher=f"""
            MATCH (:Compliance)-[:COMPLIANCE]->(c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)
            RETURN v.date AS version
        """
        results = graph.run(cypher)
        for result in results:
            version_date = result['version'].isoformat()
            response.append({'version': version_date})

    return response

# 컴플라이언스에 맞는 article 가져오기
def get_article(dict):
    compliance = dict['compliance_selected']
    version=str(dict['version_selected'])
    response=[]

    if compliance and version and version!='none':
        cypher=f"""
            OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:CHAPTER]->(:Chapter)-[:SECTION]->(:Section)-[:ARTICLE]->(a:Article)
            WITH a
            WHERE a IS NOT NULL AND v.date = date('{version}')
            RETURN a.no AS no, a.name AS name ORDER BY a.no

            UNION

            OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:CHAPTER]->(:Chapter)-[:ARTICLE]->(a:Article)
            WITH a
            WHERE a IS NOT NULL AND v.date = date('{version}')
            RETURN a.no AS no, a.name AS name ORDER BY a.no

            UNION

            OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:ARTICLE]->(a:Article)
            WITH a
            WHERE a IS NOT NULL AND v.date = date('{version}')
            RETURN a.no AS no, a.name AS name ORDER BY a.no
        """

        results = graph.run(cypher)
        for result in results:
            response.append({'no':result['no'], 'name': result['name']})
        
    return response

# data 목록 가져오기
def get_data(search_query1=None, search_query2=None):
    response=[]
    if not search_query1 and not search_query2:
        cypher=f"""
            MATCH (p:Product:Evidence:Compliance)-[:DATA]->(d:Data:Compliance:Evidence)
            RETURN d AS data, p AS product
        """

        results = graph.run(cypher)
        for result in results:
            response.append(result) 

    else:
        cypher=f"""
            MATCH (p:Product:Evidence:Compliance)-[:DATA]->(d:Data:Compliance:Evidence)
            WHERE toLower(d.{search_query1}) CONTAINS toLower('{search_query2}')
            RETURN d AS data, p AS product
        """
        results = graph.run(cypher)
        for result in results:
            response.append(result)

    return response


# data 추가
def add_data(dict):
    product_selected= dict.get('product_selected', '')
    name = dict.get('name', '')
    comment = dict.get('comment', '')
    author = dict.get('author', '')
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    compliance = dict.get('compliance', '')
    version_selected=dict.get('version_selected', '')
    article_selected = dict.get('article_selected', '')

    if not name:                         
        return 'NULL'


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
    if article_selected!='none' and article_selected: 
        #article까지 selected 했을 때
        cypher= f"""
                MATCH (e:Compliance:Evidence{{name:'Evidence'}})-[:PRODUCT]->(p:Product:Evidence{{name:'{product_selected}'}})
                MATCH (v:Version{{name:'{compliance}', date:date('{version_selected}')}})-[*]->(a:Article{{compliance_name:'{compliance}', no:'{article_selected}'}})
                MERGE (p)-[:DATA]->
                    (d:Data:Compliance:Evidence {{
                    name:'{name}',
                    comment:'{comment}',
                    author:'{author}',
                    last_update:'{last_update}'
                }})-[:EVIDENCE]->(a)
                RETURN COUNT(d)
            """

    elif compliance!='none' and compliance: 
    # 컴플라이언스만 selected 했을 때
        cypher= f"""
                MATCH (e:Compliance:Evidence{{name:'Evidence'}})-[:PRODUCT]->(p:Product:Evidence{{name:'{product_selected}'}})
                MATCH (c:Version:Compliance{{name:'{compliance}', date:date('{version_selected}')}})
                MERGE (p)-[:DATA]->
                    (d:Data:Compliance:Evidence {{
                    name:'{name}',
                    comment:'{comment}',
                    author:'{author}',
                    last_update:'{last_update}'
                }})-[:EVIDENCE]->(c)
                RETURN COUNT(d)
            """  
        
    #매핑할 애들이 없을 때(그냥 증적 노드만 생성)
    else: 
        cypher= f"""
                MATCH (e:Compliance:Evidence{{name:'Evidence'}})-[:PRODUCT]->(p:Product:Evidence{{name:'{product_selected}'}})
                MERGE (p)-[:DATA]->
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

def mod_data(dict):
    last_name=dict.get('last_name', '')
    name = dict.get('mod_name', '')
    comment = dict.get('mod_comment', '')
    author = dict.get('mod_author', '')
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not name:
        return 'NULL'

    if last_name == name:
        #data name을 수정하는 게 아니라면
        cypher= f"""
            MATCH (d:Data:Compliance{{name:'{last_name}'}})
            SET d.comment='{comment}', d.author='{author}', d.last_update='{last_update}' 
            RETURN COUNT(d)
        """
    else:
        #data name도 수정하는거라면 중복체크 필요
        cypher=f"""
            MATCH (c:Data:Compliance:Evidence{{
                name:'{name}'
            }})
            RETURN count(c)
        """
        if graph.evaluate(cypher) >= 1:
            return 'already exist'

        cypher= f"""
            MATCH (d:Data:Compliance{{name:'{last_name}'}})
            SET d.name='{name}', d.comment='{comment}', d.author='{author}', d.last_update='{last_update}' 
            RETURN COUNT(d)
        """

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'


# data 삭제
def del_data(dict):
    name=dict['name']
    if not name:
        return 'fail'

    #하위 노드가 있을 경우 하위 노드(파일)까지 모두 삭제, 아니면 Data만 삭제
    cypher=f"""
        MATCH (d:Compliance:Evidence:Data{{name:'{name}'}})
        WITH d
        OPTIONAL MATCH (d)-[:FILE]->(f:File:Compliance:Evidence)
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


# file 리스트 가져오기
def get_file(data=None):
    if data==None:
        return "잘못된 데이터"
    else:
        data=graph.evaluate(f"""
            MATCH (d:Data:Compliance:Evidence{{name:'{data}'}})-[:FILE]->(file:File:Compliance:Evidence)
            RETURN collect(file)
        """)

    return data


# file 추가
def add_file(dict):
    data_name=dict['data_name']
    name=dict['name']
    comment=dict['comment']
    author=dict['author']
    version=dict['version']
    poc=dict['poc']
    upload_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if name=='':
        return 'NULL'

    #중복체크
    cypher=f"""
        MATCH (d:Data:Evidence:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{name}'}})
        RETURN count(f)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    cypher= f"""
        MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})
        MERGE (d)-[:FILE]->(f:File:Compliance:Evidence {{
            name:'{name}',
            comment:'{comment}',
            author:'{author}',
            poc:'{poc}',
            version:'{version}',
            upload_date:'{upload_date}'
        }})
        SET d.last_update='{upload_date}'
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
    
def mod_file(dict):
    data_name=dict.get('data_name', '')
    last_name=dict.get('last_name', '')
    name = dict.get('mod_name', '')
    comment = dict.get('mod_comment', '')
    author = dict.get('mod_author', '')
    version = dict.get('mod_version', '')
    poc = dict.get('mod_poc', '')
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not name:
        return 'NULL'

    if last_name == name:
        #data name을 수정하는 게 아니라면
        cypher= f"""
            MATCH (d:Data:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{last_name}'}})
            SET f.comment='{comment}', 
                f.author='{author}', 
                f.version='{version}',
                f.poc='{poc}',
                f.last_update='{last_update}',
                d.last_update='{last_update}'
            RETURN COUNT(f)
        """
    else:
        #data name도 수정하는거라면 중복체크 필요
        cypher=f"""
            MATCH (d:Data:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{name}'}})
            RETURN count(f)
        """
        if graph.evaluate(cypher) >= 1:
            return 'already exist'

        cypher= f"""
            MATCH (d:Data:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{last_name}'}})
            SET f.name='{name}',
                f.comment='{comment}', 
                f.author='{author}', 
                f.version='{version}',
                f.poc='{poc}',
                f.last_update='{last_update}',
                d.last_update='{last_update}'
            RETURN COUNT(f)
        """

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return author
        #return 'fail'


# file 삭제
def del_file(dict):
    data_name=dict['data_name']
    file_name=dict['file_name']
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    cypher= f"""
        MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence {{name:'{file_name}'}})
        DETACH DELETE f
        SET d.last_update='{last_update}'
        RETURN count(f)
    """

    try:
        if 1 == graph.evaluate(cypher):
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'



# 컴플라이언스와 증적 파일이 매핑된 애들을 갖고 오기
def get_compliance_list(search_cate=None, search_content=None):
    response=[]
    
    if search_cate=="com":
        cypher=f"""
            MATCH (com:Compliance{{name:'{search_content}'}})-[:VERSION]->(ver:Version)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)
            RETURN com, ver, chap, sec, arti ORDER BY arti.no
        """
    elif search_cate=="evi":
        cypher=f"""
            MATCH (ver:Version:Compliance)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
            RETURN ver, chap, sec, arti ORDER BY arti.no

            UNION

            MATCH (ver:Version:Compliance)-[:CHAPTER]->(chap:Chapter)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
            RETURN ver, chap, '' AS sec, arti ORDER BY arti.no

            UNION

            MATCH (ver:Version:Compliance)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
            RETURN ver, '' AS chap, '' AS sec, arti ORDER BY arti.no

            UNION

            MATCH (ver:Version:Compliance)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
            RETURN ver, '' AS chap, '' AS sec, '' AS arti

        """

    results = graph.run(cypher)
    for result in results:
     response.append(result)

    return response


# File 페이지 내 Compliance 추가
def add_com(dict):
    data_name = dict.get('name', '')
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    compliance = dict.get('compliance', '')
    version_selected = dict.get('version_selected', '')
    article_selected = dict.get('article_selected', '')

    if not version_selected or not compliance:
        return 'NULL'       

    #매핑 리스트가 있을 때(컴플라이언스와 관계 생성)
    if article_selected!='none' and article_selected: 
        #article까지 selected 했을 때
        cypher= f"""
                MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})
                MATCH (a:Article:Compliance{{compliance_name:'{compliance}', no:'{article_selected}'}})
                MERGE (d)-[:EVIDENCE]->(a)
                SET d.last_update='{last_update}'
                RETURN COUNT(d)
            """
    elif compliance!='none': 
    # 컴플라이언스만 selected 했을 때
        cypher= f"""
                MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})
                MATCH (v:Version:Compliance{{name:'{compliance}', date:date('{version_selected}')}})
                MERGE (d)-[:EVIDENCE]->(v)
                SET d.last_update='{last_update}'
                RETURN COUNT(d)
            """  
    else: 
        return 'fail'

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'

def add_integration(dict):
    product = dict.get('product', '')

    if not product:
        return 'NULL'

    #중복 체크 필요
    cypher=f"""
        MATCH (c:Product:Compliance:Evidence{{
            name:'{product}'
        }})
        RETURN count(c)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'
        
        
    cypher= f"""
            MATCH (e:Compliance:Evidence{{name:'Evidence'}})
            MERGE (e)-[:PRODUCT]->
                (p:Product:Compliance:Evidence {{
                name:'{product}'
            }})
            RETURN COUNT(p)
        """

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'
    
def get_product():
    response=[]

    cypher=f"""
        MATCH (product:Product:Compliance:Evidence)
        RETURN product.name AS name ORDER BY toLower(product.name)
    """
    
    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response







    



