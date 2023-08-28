from django.shortcuts import HttpResponse
from django.conf import settings
from py2neo import Graph
from .alert import get_relation_json, get_node_json
import json

## LOCAL
# graph = Graph("bolt://127.0.0.1:7687", auth=('neo4j', 'teiren001'))

## NCP
# host = settings.NEO4J_HOST
# port = settings.NEO4J_PORT
# password = settings.NEO4J_PASSWORD
# username = settings.NEO4J_USERNAME

## AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))


# 사용자별 위협 분석
def get_user_visuals():
    cypher = f"""
    MATCH (a:Account)
    WITH a.name as account
    OPTIONAL MATCH p=(r:RULE)<-[d:DETECTED]-(l:LOG)
    WHERE l.userIdentity_type = account 
    WITH account, p
    CALL apoc.do.when(
        p IS NULL,
        "MATCH (r:RULE)<-[d:DETECTED]-(l:LOG) WHERE l.userIdentity_userName = account RETURN account, count(d) as count, COLLECT(r)[-1] as rule, COLLECT(l)[-1] as log",
        "MATCH (r:RULE)<-[d:DETECTED]-(l:LOG) WHERE l.userIdentity_type = account  RETURN account, count(d) as count, COLLECT(r)[-1] as rule, COLLECT(l)[-1] as log",
        {{account:account}}
    ) YIELD value
    WITH DISTINCT(value)
    RETURN
        HEAD([label IN labels(value.log) WHERE label <> 'LOG']) AS cloud,
        CASE
            WHEN value.account CONTAINS 'vulnerable' THEN split(value.account,'_')[0]
            ELSE value.account
        END as account,
        value.account as account_real,
        value.count as total,
        value.rule.ruleName as recent_detection,
        value.log.eventName as recent_action,
        apoc.date.format(apoc.date.parse(value.log.eventTime, "ms", "yyyy-MM-dd'T'HH:mm:ssX"), "ms", "yyyy-MM-dd HH:mm:ss") AS recent_time
    ORDER BY total DESC
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        response.append(dict(result.items()))
    return response

# 사용자 중심 분석 그래프 시각화
def user_graph(request):
    if isinstance(request, dict) :
        data = get_user_node(request)
        data += get_user_relation(request)
        table = get_user_table(request)
        context = {'graph': json.dumps(data), 'table': table }
        return context
    return HttpResponse('다시 시도')

def get_user_node(request):
    account = request['account']
    cloud = request['cloud']
    cypher = f"""
    OPTIONAL MATCH p=(r:RULE:{cloud})<-[d:DETECTED]-(l:LOG)<-[:ACTED*4]-(f)
    WHERE l.userIdentity_type = '{account}'
    WITH p, '{account}' as account
    CALL apoc.do.when(
        p IS NULL,
        "MATCH p=(r:RULE)<-[d:DETECTED]-(l:LOG)<-[:ACTED*4]-(f) WHERE l.userIdentity_userName = account  RETURN p, f",
        "MATCH p=(r:RULE)<-[d:DETECTED]-(l:LOG)<-[:ACTED*4]-(f) WHERE l.userIdentity_type = account RETURN p, f",
        {{account:account}}
    ) YIELD value
    WITH DISTINCT(value), account
    MATCH (a:Account {{name:account}})
    UNWIND NODES(value.p) as nodes
    RETURN DISTINCT(nodes), a
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        nodes = dict(result.items())
        for node in nodes.values():
            response.append(get_node_json(node, cloud))
    return response

def get_user_relation(request):
    account = request['account']
    cloud = request['cloud']
    global graph
    cypher = f"""
    OPTIONAL MATCH p=(r:RULE:{cloud})<-[d:DETECTED]-(l:LOG)<-[:ACTED|CONNECTED*3]-(f)
    WHERE l.userIdentity_type = '{account}' 
    WITH p, '{account}' as account
    CALL apoc.do.when(
        p IS NULL,
        "MATCH p=(r:RULE)<-[d:DETECTED]-(l:LOG)<-[:ACTED|CONNECTED*3]-(f) WHERE l.userIdentity_userName = account  RETURN p, f",
        "MATCH p=(r:RULE)<-[d:DETECTED]-(l:LOG)<-[:ACTED|CONNECTED*3]-(f) WHERE l.userIdentity_type = account  RETURN p, f",
        {{account:account}}
    ) YIELD value
    WITH DISTINCT(value), account
    MATCH (a:Account {{name:account}})
    CALL apoc.create.vRelationship(a, 'ACTED', {{}}, value.f) YIELD rel AS temp_rel
    UNWIND RELATIONSHIPS(value.p) as rels
    WITH DISTINCT(rels) as rel, temp_rel
    WITH [
            PROPERTIES(rel),
            ID(rel),
            ID(STARTNODE(rel)),
            id(ENDNODE(rel)),
            TYPE(rel)
        ] as relation,
        [
            PROPERTIES(temp_rel),
            ID(temp_rel), 
            ID(STARTNODE(temp_rel)), 
            ID(ENDNODE(temp_rel)), 
            TYPE(temp_rel)
        ] as temp_rel
    RETURN COLLECT(relation) as relations, temp_rel
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for relation in data['relations']:
            response.append(get_relation_json(relation))
        response.append(get_relation_json(data['temp_rel']))
    return response

def get_user_table(request):
    account = request['account']
    global graph
    cypher = f"""
    OPTIONAL MATCH p=(r:RULE:AWS)-[d:DETECTED]->(l:LOG)<-[:ACTED|CONNECTED]-()
    WHERE l.userIdentity_type = '{account}' 
    WITH p, '{account}' as account
    CALL apoc.do.when(
        p IS NULL,
        "MATCH p=(r:RULE)-[d:DETECTED]->(l:LOG)<-[:ACTED|CONNECTED]-() WHERE l.userIdentity_userName = account  RETURN d, l, r",
        "MATCH p=(r:RULE)-[d:DETECTED]->(l:LOG)<-[:ACTED|CONNECTED]-() WHERE l.userIdentity_type = account  RETURN d, l, r",
        {{account:account}}
    ) YIELD value
    WITH DISTINCT(value) AS value
    RETURN
        DISTINCT(ID(value.d)) AS id,
        value.r.ruleName AS detected_rule,
        value.l.eventTime AS eventTime,
        apoc.date.format(apoc.date.parse(value.l.eventTime, "ms", "yyyy-MM-dd'T'HH:mm:ssX"), "ms", "yyyy-MM-dd HH:mm:ss") AS detected_time,
        CASE
            WHEN size(split(value.r.eventSource, ',')) > 1 THEN 'FLOW'
            ELSE split(value.r.eventSource, '.')[0]
        END AS rule_type,
        [label IN LABELS(value.l) WHERE label <> 'LOG'][0] AS cloud
    ORDER BY detected_time DESC
    """
    results = graph.run(cypher).data()
    response = []
    for result in results:
        node = dict(result.items())
        arr = {'account': account}
        arr.update(node)
        node.update({'arr': json.dumps(arr)})
        response.append(node)
    return response