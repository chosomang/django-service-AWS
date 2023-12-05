from django.conf import settings
from py2neo import Graph
from datetime import datetime

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))


def get_articles_of_association(search_query1=None, search_query2=None):
    response=[]
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'Articles of Association'}})-[:DATA]->(d:Data:Evidence)
        RETURN d as data
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_regulation(search_query1=None, search_query2=None):
    response=[]
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'Regulation'}})-[:DATA]->(d:Data:Evidence)
        RETURN d as data
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_guidelines(search_query1=None, search_query2=None):
    response=[]
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'Guidelines'}})-[:DATA]->(d:Data:Evidence)
        RETURN d as data
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_rules(search_query1=None, search_query2=None):
    response=[]
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'Rules'}})-[:DATA]->(d:Data:Evidence)
        RETURN d as data
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_document(search_query1=None, search_query2=None):
    response=[]
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'Document'}})-[:DATA]->(d:Data:Evidence)
        RETURN d as data
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response

def get_etc(search_query1=None, search_query2=None):
    response=[]
    cypher=f"""
        MATCH (:Evidence:Compliance)-[:PRODUCT]->(:Product{{name:'Policy Manage'}})-[:POLICY]->(p:Policy{{name:'ETC'}})-[:DATA]->(d:Data:Evidence)
        RETURN d as data
    """

    results = graph.run(cypher)
    for result in results:
        response.append(result)
    
    return response



    



