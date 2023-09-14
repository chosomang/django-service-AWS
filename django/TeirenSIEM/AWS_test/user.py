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
    MATCH p = (r:RULE)<-[d:DETECTED]-(l:LOG)<-[:ACTED|DATE*]-(a:Account)
    WITH DISTINCT(a.name) as account, count(d) as count, COLLECT(r)[-1] as rule, COLLECT(l)[-1] as log
    RETURN
        HEAD([label IN LABELS(log) WHERE label <> 'LOG' AND label <> 'IAM' AND label <> 'Role']) AS cloud,
        CASE
            WHEN account CONTAINS 'cgid' THEN SPLIT(account, '_')[-1]
            ELSE account
        END AS account,
        account AS account_real,
        count AS total,
        rule.ruleName AS recent_detection,
        log.eventName AS recent_action,
        apoc.date.format(apoc.date.parse(log.eventTime, "ms", "yyyy-MM-dd'T'HH:mm:ssX"), "ms", "yyyy-MM-dd HH:mm:ss") AS recent_time
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
    MATCH (a:Account {{name:'{account}'}})
    CALL apoc.path.expandConfig(a, {{
        relationshipFilter: "DETECTED|ACTED|DATE",
        labelFilter: "/RULE",
        minLevel: 1,
        maxLevel: 10000}}) YIELD path
    UNWIND NODES(path) as nodes
    RETURN DISTINCT(nodes)
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
    global graph
    cypher = f"""
    MATCH (a:Account {{name:'{account}'}})
    CALL apoc.path.expandConfig(a, {{
        relationshipFilter: "DETECTED|ACTED|DATE",
        labelFilter: "/RULE",
        minLevel: 1,
        maxLevel: 10000}}) YIELD path
    UNWIND RELATIONSHIPS(path) as rels
    WITH DISTINCT(rels) as rel
    WITH DISTINCT(rel)
    WITH [
            PROPERTIES(rel),
            ID(rel),
            ID(STARTNODE(rel)),
            id(ENDNODE(rel)),
            TYPE(rel)
        ] as relation
    RETURN COLLECT(relation) as relations
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for relation in data['relations']:
            response.append(get_relation_json(relation))
    return response

def get_user_table(request):
    account = request['account']
    global graph
    cypher = f"""
    MATCH p=(r:RULE)<-[d:DETECTED]-(l:LOG)<-[:ACTED|DATE*]-(a:Account {{name:'{account}'}})
    RETURN
        DISTINCT(ID(d)) AS id,
        r.ruleName AS detected_rule,
        l.eventTime AS eventTime,
        apoc.date.format(apoc.date.parse(l.eventTime, "ms", "yyyy-MM-dd'T'HH:mm:ssX"), "ms", "yyyy-MM-dd HH:mm:ss") AS detected_time,
        CASE
            WHEN size(split(r.eventSource, ',')) > 1 THEN 'FLOW'
            ELSE split(r.eventSource, '.')[0]
        END AS rule_type,
        [label IN LABELS(l) WHERE label <> 'LOG'][0] AS cloud
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