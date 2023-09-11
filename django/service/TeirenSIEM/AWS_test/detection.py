from django.conf import settings
from django.shortcuts import render, HttpResponse
from py2neo import Graph
from TeirenSIEM.graphdb import neo4j_graph as ncp
import json

## AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def neo4j_graph(request):
    if isinstance(request, dict) :
        if request['cloud'] == 'NCP':
            context = ncp(request)
            return context
        data = get_node(request)
        data += get_relation(request)
        details = get_log_details(request)
        context = {'graph': json.dumps(data), 'details': details }
        return context
    elif request.method == 'POST':
        context = dict(request.POST.items())
        if context['cloud'] == 'NCP':
            context = ncp(request)
            return context
        data = get_data(context)
        details = get_log_details(context)
        context.update({'graph': json.dumps(data), 'details': details})
        return render(request, 'graphdb/graph.html', context)
    return HttpResponse('다시 시도')


# Node cytoscape.js 형태로 만들기
def get_node_json(node, cloud):
    data = {
        "id" : node.identity,
        "name" : "",
        "score" : 400,
        "query" : True,
        "gene" : True
    }
    property = dict(node.items())
    property = {key:property[key] for key in sorted(property.keys())}
    if node.has_label('LOG'):
        data['label'] = 'LOG'
        for key, value in property.items():
            if key == 'eventName':
                data['name'] = value
            else:
                if 'responseElements' in key or 'requestParameters' in key or 'tls' in key:
                    continue
                if 'userAgent' in key:
                    continue
                # if '' in key:
                #     continue
                if 'errorMessage' in key:
                    value = value.replace('\'', '[',1)
                    value = value.replace('\'', ']',1)
                if '\'' in str(value):
                    value = value.replace('\'', '[',1)
                    value = value.replace('\'', ']',1)
                data[key] = value
    else:
        if node.has_label('IP'):
            data['name'] = property['ipAddress']
        if node.has_label('Date'):
            data['label'] = 'Date'
        if node.has_label('Account'):
            data['label'] = 'Account'
            data['score'] = 700
        if node.has_label('RULE'):
            data['label'] = 'RULE'
            data['name'] = property['ruleName']
        for key, value in property.items():
            if key == 'name':
                value = value.split('_')[0]
            if 'responseElements' in key or 'requestParameters' in key or 'tls' in key:
                continue
            if 'errorMessage' in key:
                value = value.replace('\'', '[',1)
                value = value.replace('\'', ']',1)
            if key == 'date':
                value = str(value)
                data['name'] = value
            data[key] = value
    response = {
        "data": data,
        "group" : "nodes"
    }
    return response


def get_data(request):
    rule_type = request['rule_type']
    if rule_type == 'default':
        data = get_default(request)
    else:
        data = get_flow(request)
    return data

# Default Rule
def get_default(request):
    detected_rule = request['detected_rule']
    eventTime = request['eventTime']
    cloud = request['cloud']
    id = request['id']
    cypher = f"""
    MATCH (rule:RULE:{cloud} {{ruleName: '{detected_rule}'}})<-[detect:DETECTED]-(log:LOG:{cloud} {{eventTime:'{eventTime}'}})
    WHERE ID(detect) = {id}
    WITH rule, detect, log
    OPTIONAL MATCH p=(log)<-[:ACTED*..5]-(view:LOG)
    WITH p, rule, detect, log
    CALL apoc.do.when(
        p IS NULL,
        "MATCH p=(rule)<-[detect]-(log)<-[:ACTED]-(:Date)<-[:DATE]-(:Account)
            RETURN NODES(p) as nodes, RELATIONSHIPS(p) AS relations",
        "MATCH p=(rule)<-[detect]-(log)<-[:ACTED*..5]-(view:LOG)
            WITH rule, log, COLLECT(view) as view, RELATIONSHIPS(COLLECT(p)[-1]) as relations
            RETURN [rule,log]+view AS nodes, relations",
        {{rule:rule, log:log, detect:detect}}
    ) YIELD value
    WITH COLLECT(value)[-1] as value
    WITH value.nodes as nodes, value.relations as relations, value.nodes[-1] as last
    OPTIONAL MATCH (last)<-[acted:ACTED*]-(date:Date)<-[date_rel:DATE]-(account:Account)
    WITH last, date, date_rel, acted, size(acted) as acted_cnt,
        CASE 
            WHEN date IS NULL THEN nodes
            ELSE nodes+[date, account]
        END AS nodes,
        CASE
            WHEN date_rel IS NULL THEN relations
            ELSE relations+[date_rel]
        END AS relations
    CALL apoc.do.when(
        acted_cnt > 1,
        "   MATCH p=(last)<-[:ACTED*]-(mid)
            WITH date, last, mid.eventName AS eventName, COUNT(mid) AS cnt, p
            WITH apoc.map.fromPairs(COLLECT([eventName,cnt])) as prop, p, last, date
            CALL apoc.create.vNode(['Analysis'], apoc.map.merge(prop,{{name:'Analysis'}})) YIELD node AS analysis
            CALL apoc.create.vRelationship(date,'ANALYZE',{{}}, analysis) YIELD rel AS analyze1
            CALL apoc.create.vRelationship(analysis,'ANALYZE',{{}}, last) YIELD rel AS analyze2
            RETURN analysis, [analyze1, analyze2] as analyze",
        "   WITH CASE
                WHEN acted IS NULL THEN []
                ELSE acted
            END AS acted
            return [] as analysis, acted as analyze",
        {{date:date, last:last, acted:acted}}
    ) YIELD value
    WITH COLLECT(value)[-1].analysis AS analysis, COLLECT(value)[-1].analyze AS analyze, nodes, relations
    UNWIND relations+analyze AS relation
    WITH DISTINCT(relation) AS relation, nodes + analysis AS nodes
    WITH nodes,
        [
            PROPERTIES(relation),
            ID(relation),
            ID(STARTNODE(relation)),
            ID(ENDNODE(relation)),
            TYPE(relation)
        ] AS relation
    RETURN nodes,COLLECT(relation) AS relations
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for node in data['nodes']:
            response.append(get_node_json(node, cloud))
        for relation in data['relations']:
            response.append(get_relation_json(relation))
    return response

# Flow Rule
def get_flow(request):
    detected_rule = request['detected_rule']
    eventTime = request['eventTime']
    cloud = request['cloud']
    id = request['id']
    cypher = f"""
    
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for node in data['nodes']:
            response.append(get_node_json(node, cloud))
        for relation in data['relations']:
            response.append(get_relation_json(relation))
    return response
    return 0


# Node 내용
def get_node(request):
    detected_rule = request['detected_rule']
    eventTime = request['eventTime']
    cloud = request['cloud']
    id = request['id']
    global graph
    cypher = f"""
    MATCH p=(r:RULE {{ruleName:'{detected_rule}'}})<-[d:DETECTED]-(l:LOG {{eventTime:'{eventTime}'}})<-[:ACTED|DATE*]-(a:Account)
    WHERE ID(d) = {id}
    UNWIND NODES(p) as nodes
    WITH COLLECT(DISTINCT(nodes)) as nodes
    RETURN nodes
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for node in data['nodes']:
            response.append(get_node_json(node, cloud))
    return response

# Relationship cytoscape.js 형태로 만들기
def get_relation_json(relation):
    data = {
        "source" : relation[2],
        "target" : relation[3],
        "weight" : 1,
        "group" : "coexp",
        "id" : "e"+str(relation[1]),
        "name": relation[4]
    }
    response = {
        "data" : data,
        "group" : "edges"
    }
    return response

# Relationship 내용
def get_relation(request):
    detected_rule = request['detected_rule']
    eventTime = request['eventTime']
    cloud = request['cloud']
    id = request['id']
    global graph
    cypher = f"""
    MATCH p=(r:RULE {{ruleName:'{detected_rule}'}})<-[d:DETECTED]-(l:LOG {{eventTime:'{eventTime}'}})<-[:ACTED|DATE*]-(a:Account)
    WHERE ID(d) = {id}
    UNWIND RELATIONSHIPS(p) as rel
    WITH DISTINCT(rel) as rel
    WITH
        [
            PROPERTIES(rel),
            ID(rel),
            ID(STARTNODE(rel)),
            ID(ENDNODE(rel)),
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

# 로그 디테일
def get_log_details(request):
    detected_rule = request['detected_rule']
    eventTime = request['eventTime']
    cloud = request['cloud']
    id = request['id']
    global graph
    cypher = f"""
    MATCH p=(r:RULE{{ruleName:'{detected_rule}'}})<-[d:DETECTED]-(l:LOG {{eventTime:'{eventTime}'}})<-[:ACTED|DATE*]-(a:Account)
    WHERE ID(d) = {id}
    UNWIND NODES(p) as node
    WITH DISTINCT(node) as node, l, r, a
    WHERE node <> r AND node <> a AND NOT 'Date' IN LABELS(node)
    RETURN
        ID(node) AS id,
        node.eventTime as eventTime,
        node.eventName as productName,
        split(node.eventSource, '.')[0] as actionType,
        node.eventType as resultType,
        node.sourceIPAddress as sourceIP,
        CASE
            WHEN node = l THEN 'detected'
            ELSE 'normal'
        END AS type
    """
    results = graph.run(cypher).data()
    response = []
    for result in results:
        node = dict(result.items())
        node['cloud'] = cloud
        response.append(node)
    return response