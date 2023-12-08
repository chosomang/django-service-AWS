from django.conf import settings
from py2neo import Graph
from datetime import datetime

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def get_policy(search_query1=None, search_query2=None):
    response=[]

    if search_query1=='policy' and search_query2:
        cypher=f"""
            MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
            OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
            WHERE toLower(p.name) CONTAINS toLower('{search_query2}')
            RETURN p AS policy, COLLECT(d) AS data
            ORDER BY policy.name ASC;
        """
    elif search_query1=='data' and search_query2:
        cypher=f"""
            MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
            OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
            WHERE toLower(d.name) CONTAINS toLower('{search_query2}')
            RETURN p AS policy, COLLECT(d) AS data
            ORDER BY policy.name ASC;
        """
    else:
        cypher=f"""
            MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy)
            OPTIONAL MATCH (p)-[:DATA]->(d:Data:Evidence:Compliance)
            RETURN p AS policy, COLLECT(d) AS data
            ORDER BY policy.name ASC;
        """

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

def add_policy(policy_name):
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
    
def add_policy_data(dict):
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
    


