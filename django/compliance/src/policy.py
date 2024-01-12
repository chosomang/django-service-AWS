from django.conf import settings
from py2neo import Graph
from datetime import datetime

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))


def get_policy_data_list(request):
    try:
        response=[]
        main_search_key = request.POST.get('main_search_key', '')
        main_search_value = request.POST.get('main_search_value', '')

        if main_search_key == 'policy' and main_search_value:
            cypher=f"""
                MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
                WHERE toLower(p.name) CONTAINS toLower('{main_search_value}')
                OPTIONAL MATCH (policy)-[:DATA]->(d:Data:Evidence:Compliance)
                RETURN p AS policy, COLLECT(d) AS data
                ORDER BY policy.name ASC
            """
        elif main_search_key == 'data' and main_search_value:
            cypher=f"""
                MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
                MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
                WHERE toLower(d.name) CONTAINS toLower('{main_search_value}')
                RETURN p AS policy, COLLECT(d) AS data
                ORDER BY policy.name ASC
            """
        else:
            cypher=f"""
                MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
                OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
                RETURN p AS policy, COLLECT(d) AS data
                ORDER BY policy.name ASC
            """
        results = graph.run(cypher)
        for result in results:
            response.append(result)
    except Exception as e:
        print(e)
        response = []
    finally:
        return response

def add_policy(request):
    try:
        policy = request.POST.get('policy','')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not policy:
            response = "Please Enter Policy Name"
        elif 0 < graph.evaluate(f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{policy}'}})
        RETURN COUNT(p)
        """):
            response = "Policy Already Exists. Please Enter New Policy Name"
        else:
            graph.run(f"""
            MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})
            MERGE (p:Policy:Evidence:Compliance {{name:'{policy}', last_update:'{timestamp}'}})
            MERGE (product)-[:POLICY]->(p)
            """)
            response = "Successfully Created Policy"
    except Exception as e:
        print(e)
        response = "Failed To Create Policy. Please Try Again."
    finally:
        return response

def modify_policy(request):
    try:
        og_policy = request.POST.get('og_policy', '')
        policy = request.POST.get('policy', '')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not og_policy:
            raise Exception
        elif not policy:
            response = "Please Enter Policy Name"
        elif 0 < graph.evaluate(f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{policy}'}})
        RETURN COUNT(p)
        """):
            response = "Policy Already Exists. Please Enter New Policy Name"
        else:
            graph.evaluate(f"""
            MATCH (:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{og_policy}'}})
            SET p.name = '{policy}',
                p.last_update = '{timestamp}'
            """)
            response = "Successfully Modified Policy"
    except Exception as e:
        print(e)
        response ="Failed To Modify Policy. Please Try Again."
    finally:
        return response

def delete_policy(request):
    try:
        policy = request.POST.get('policy', '')
        if not policy:
            raise Exception
        else:
            graph.evaluate(f"""
            MATCH (:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{policy}'}})
            OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
            OPTIONAL MATCH (d)-[:FILE]->(f:File:Evicence:Compliance)
            DETACH DELETE p
            DETACH DELETE d
            DETACH DELETE f
            """)
            response = 'Successfully Deleted Policy'
    except Exception as e:
        print(e)
        response = 'Failed To Delete Policy. Please Try Again.'
    finally:
        return response

def add_policy_data(request):
    for key, value in request.POST.dict().items():
        if not value:
            return f"Please Enter/Select Data {key.title()}"
    try:
        policy = request.POST.get('policy', '')
        name = request.POST.get('name', '')
        comment = request.POST.get('comment', '')
        author = request.POST.get('author', '')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 0 < graph.evaluate(f"""
        MATCH (:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{policy}'}})-[:DATA]->(d:Data {{name:'{name}'}})
        RETURN COUNT(d)
        """):
            response = "Policy Data Name Already Exists. Please Enter New Policy Data Name."
        else:
            graph.evaluate(f"""
            MATCH (:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{policy}'}})
            MERGE (d:Data:Evidence:Compliance {{name:'{name}', comment:'{comment}', author:'{author}', last_update:'{timestamp}'}})
            MERGE (p)-[:DATA]->(d)
            """)
            response = "Successfully Added Policy Data"
    except Exception as e:
        print(e)
        response ="Failed To Add Policy Data. Please Try Again."
    finally:
        return response

def modify_policy_data(request):
    print(request.POST.dict())
    for key, value in request.POST.dict().items():
        if not value and key not in ['og_name']:
            return f"Please Enter/Select Data {key.title()}"
    try:
        policy = request.POST.get('policy', '')
        name = request.POST.get('name', '')
        og_name = request.POST.get('og_name', '')
        comment = request.POST.get('comment', '')
        author = request.POST.get('author', '')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if og_name != name and 0 < graph.evaluate(f"""
        MATCH (:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{policy}'}})-[:DATA]->(d:Data {{name:'{name}'}})
        RETURN COUNT(d)
        """):
            response = "Policy Data Name Already Exists. Please Enter New Policy Data Name."
        else:
            graph.evaluate(f"""
            MATCH (:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy {{name:'{policy}'}})-[:DATA]->(d:Data {{name:'{og_name}'}})
            SET d.name = '{name}',
                d.comment = '{comment}',
                d.author = '{author}',
                d.last_update = '{timestamp}'
            """)
            response = "Successfully Modified Policy Data"
    except Exception as e:
        print(e)
        response ="Failed To Modify Policy Data. Please Try Again."
    finally:
        return response

def delete_policy_data(request):
    print(request.POST.dict())
    # for key, value in request.POST.dict().items():
    #     if not value:
    #         return f"Please Enter/Select Data {key.title()}"
    try:
        response = "test"
    except Exception as e:
        print(e)
        response ="Failed To . Please Try Again."
    finally:
        return response

# def test(request):
#     print(request.POST.dict())
#     try:
#         response = "test"
#     except Exception as e:
#         print(e)
#         response ="Failed To . Please Try Again."
#     finally:
#         return response
#------------------------------------------------------------------------------------
def get_policy(search_query1=None, search_query2=None):
    response=[]

    if search_query1=='policy' and search_query2:
        cypher=f"""
            MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
            OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
            WHERE toLower(p.name) CONTAINS toLower('{search_query2}')
            RETURN p AS policy, COLLECT(d) AS data
            ORDER BY policy.name ASC
        """
    elif search_query1=='data' and search_query2:
        cypher=f"""
            MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
            OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
            WHERE toLower(d.name) CONTAINS toLower('{search_query2}')
            RETURN p AS policy, COLLECT(d) AS data
            ORDER BY policy.name ASC
        """
    else:
        cypher=f"""
            MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
            OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
            RETURN p AS policy, COLLECT(d) AS data
            ORDER BY policy.name ASC
        """
        print(cypher)
    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_policy_data(policy_name=None, data_name=None):
    response=[]

    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(policy:Policy{{name:'{policy_name}'}})-[:DATA]->(data:Data:Evidence{{name:'{data_name}'}})
        RETURN policy, data
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
        
    return response

def add_policy_og(policy_name):
    if not policy_name:                         
        return 'NULL'
    
    #중복 체크 필요
    cypher=f"""
        MATCH (p:Policy:Compliance:Evidence{{
            name:'{policy_name}'
        }})
        RETURN count(p)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})
        MERGE (product)-[:POLICY]->(policy:Policy:Evidence:Compliance{{name:'{policy_name}'}})
        RETURN COUNT(policy)
    """

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'
    
def add_policy_data_og(dict):
    policy_name=dict['policy_name']
    name=dict['data_name']
    comment=dict['data_comment']
    author=dict['data_author']
    last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if name=='':
        return 'NULL'

    #중복체크
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(:Policy{{name:'{policy_name}'}})-[:DATA]->(d:Data{{name:'{name}'}})
        RETURN count(d)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    cypher= f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'{policy_name}'}})
        MERGE (p)-[:DATA]->(d:Data:Compliance:Evidence {{
            name:'{name}',
            comment:'{comment}',
            author:'{author}',
            last_update:'{last_update}'
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
    

def add_policy_file(dict):
    policy_name=dict['policy_name']
    data_name=dict['data_name']
    name=dict['name']
    comment=dict['comment']
    author=dict['author']
    poc=dict['poc']

    upload_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if name=='':
        return 'NULL'

    #중복체크
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(:Policy{{name:'{policy_name}'}})-[:DATA]->(:Data{{name:'{data_name}'}})-[:FILE]->(f:FILE{{name:'{name}'}})
        RETURN count(f)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    cypher= f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'{policy_name}'}})-[:DATA]->(d:Data{{name:'{data_name}'}})
        MERGE (d)-[:FILE]->(f:File:Compliance:Evidence {{
            name:'{name}',
            comment:'{comment}',
            author:'{author}',
            poc:'{poc}',
            upload_date:'{upload_date}'
        }})
        SET d.last_update='{upload_date}'
        RETURN count(f)
    """
    graph.evaluate(cypher)

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'
    
def del_policy_file(dict):
    policy_name=dict['policy_name']
    data_name=dict['data_name']
    file_name=dict['file_name']

    if not data_name or not policy_name or not file_name:
        return 'fail'
    
    #하위 노드가 있을 경우 하위 노드(파일)까지 모두 삭제, 아니면 Data만 삭제
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'{policy_name}'}})-[:DATA]->(:Data{{name:'{data_name}'}})-[:FILE]->(f:File{{name:'{file_name}'}})
        DETACH DELETE f
        RETURN count(f)
    """

    try:
        if graph.evaluate(cypher) >= 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'


def del_policy_data(dict):
    policy_name=dict['policy_name']
    data_name=dict['data_name']
    
    if not data_name:
        return 'fail'

    #하위 노드가 있을 경우 하위 노드(파일)까지 모두 삭제, 아니면 Data만 삭제
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'{policy_name}'}})-[:DATA]->(d:Data{{name:'{data_name}'}})
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
    
def mod_policy_data_og(dict):
    policy_name=dict.get('policy_name', '')
    last_name=dict.get('last_name', '')
    name = dict.get('mod_name', '')
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not name or not policy_name:
        return 'NULL'

    #중복체크
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(:Policy{{name:'{policy_name}'}})-[:DATA]->(d:Data{{name:'{name}'}})
        RETURN count(d)
    """
    if graph.evaluate(cypher) >= 1:
        return 'already exist'

    cypher= f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(product:Product{{name:'Policy Manage'}})-[:POLICY]->(:Policy{{name:'{policy_name}'}})-[:DATA]->(d:Data{{name:'{last_name}'}})
        SET d.name='{name}', d.last_update='{last_update}' 
        RETURN COUNT(d)
    """

    try:
        if graph.evaluate(cypher) == 1:
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'