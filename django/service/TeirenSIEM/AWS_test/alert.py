from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from py2neo import Graph
from TeirenSIEM.graphdb import neo4j_graph as ncp
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

def get_alert_logs():
    global graph
    cypher = '''
    MATCH ()-[f:ACTED|CONNECTED]->(l:LOG)-[n:DETECTED]->(r:RULE)
    WHERE
        n.alert = 1 AND n.alert IS NOT NULL
    RETURN
        HEAD([label IN labels(l) WHERE label <> 'LOG']) AS cloud,
        l.eventTime AS detected_time,
        r.ruleComment as detectedAction,
        l.eventName as actionDisplayName,
        l.eventType as actionResultType,
        l.eventTime as eventTime,
        l.eventTime AS eventTime_format,
        l.sourceIPAddress as sourceIp,
        r.ruleName as detected_rule,
        r.ruleName+'#'+id(n) AS rule_name,
        ID(n) as id
    ORDER BY eventTime DESC
    '''
    results = graph.run(cypher)
    data = check_alert_logs()
    filter = ['cloud', 'detected_rule', 'eventTime', 'rule_name', 'id']
    for result in results:
        detail = dict(result.items())
        form = {}
        for key in filter:
            if key != 'cloud' and key != 'rule_name':
                value = detail.pop(key)
            else:
                value = detail[key]
            form[key] = value
        detail['form'] = form
        data.append(detail)
    context = {'data': data}
    return context

def check_alert_logs():
    global graph
    cypher = """
    MATCH ()-[f:ACTED|CONNECTED]->(l:LOG)-[n:DETECTED]->(r:RULE)
    WHERE
        n.alert <> 1
    RETURN
        HEAD([label IN labels(l) WHERE label <> 'LOG']) AS cloud,
        l.eventTime AS detected_time,
        r.ruleComment AS detectedAction,
        l.eventName AS actionDisplayName,
        l.eventType AS actionResultType,
        l.eventTime AS eventTime,
        l.eventTime AS eventTime_format,
        l.sourceIPAddress AS sourceIp,
        r.ruleName AS detected_rule,
        r.ruleName+'#'+id(n) AS rule_name,
        ID(n) AS id,
        n.alert AS alert
    ORDER BY alert, eventTime DESC
    """
    results = graph.run(cypher)
    data = []
    filter = ['cloud', 'detected_rule', 'eventTime', 'rule_name', 'alert', 'id']
    for result in results:
        detail = dict(result.items())
        form = {}
        for key in filter:
            if key != 'cloud' and key != 'rule_name' and key != 'alert':
                value = detail.pop(key)
            else:
                value = detail[key]
            form[key] = value
        detail['form'] = form
        data.append(detail)
    return data

# Top Bar 알림
def check_topbar_alert():
    global graph
    cypher = """
    MATCH (r:RULE)<-[n:DETECTED]-()
    WHERE n.alert = 0 OR n.alert IS NULL
    SET n.alert = CASE
            WHEN n.alert IS NULL THEN 0
            ELSE n.alert
        END
    RETURN COUNT(n) as count
    """
    count = graph.evaluate(cypher)
    if count > 0:
        response = {'top_alert':{'count': count}}
        cypher = """
        MATCH (r:RULE)<-[n:DETECTED]-(l:LOG)
        WHERE n.sent = 0 OR n.sent IS NULL
        WITH DISTINCT(n) as n, r, l
        SET n.sent = CASE
                WHEN n.sent IS NULL THEN 0
                ELSE n.sent
            END
        RETURN r, l, ID(n) as id_n
        """
        if graph.evaluate(cypher) is not None:
            results = graph.run(cypher)
            for result in results:
                cypher = f"""
                MATCH (r:RULE)<-[n:DETECTED]-(l:LOG)
                WHERE ID(r) = {result['r'].identity} AND
                    ID(l) = {result['l'].identity} AND
                    ID(n) = {result['id_n']} AND
                    (n.sent = 0 OR n.sent IS NULL)
                SET n.sent = 1
                RETURN count(n)
                """
                graph.evaluate(cypher)
                send_alert_mail(dict(result['r']), dict(result['l']), result['id_n'])
    else:
        response = {'no_top_alert': 1}
    return response

# 알림 메일
def send_alert_mail(rule, log, rel_id):
    subject = f"Teiren SIEM Rule Detection Alert Mail [{rule['ruleName']}#{rel_id}]"
    message = ''
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['chosomang12@gmail.com']
    context = {
        'r': rule,
        'rel_id': rel_id,
        'l': log,
    }
    html_message = render_to_string('risk/alert/mail.html', context)
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)

# 위협 알림 확인 후 Alert Off
def alert_off(request):
    if 'alert' in request:
        detected_rule = request['detected_rule']
        cloud = request['cloud']
        eventTime = request['eventTime']
        id = request['id']
        if cloud == 'NCP':
            global graph
            cypher = f"""
            MATCH (r:RULE:{cloud} {{name:'{detected_rule}'}})<-[n:DETECTED|FLOW_DETECTED]-(l:LOG:{cloud} {{eventTime:'{eventTime}'}})
            WHERE 
                r.is_allow = 1 AND
                n.alert IS NOT NULL AND
                n.alert = 0
            SET n.alert = 1
            RETURN count(n.alert)
            """
        elif cloud == 'AWS':
            global graph
            cypher = f"""
            MATCH (r:RULE:{cloud} {{ruleName:'{detected_rule}'}})<-[n:DETECTED]-(l:LOG:{cloud} {{eventTime:'{eventTime}'}})
            WHERE
                n.alert IS NOT NULL AND
                n.alert = 0 AND
                ID(n) = {id}
            SET n.alert = 1
            RETURN count(n.alert)
            """
        graph.evaluate(cypher)
    return request

####################################################################### Graph Visual
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
        data = get_node(context)
        data += get_relation(context)
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
    data['label'] =  list(label for label in node.labels if label != cloud and label != 'FLOW')[0]
    if node.has_label('LOG'):
        for key, value in property.items():
            if key == 'eventName':
                data['name'] = value
            else:
                data[key] = value
    else:
        if node.has_label('IP'):
            data['name'] = property['ipAddress']
        if node.has_label('Actor'):
            data['score'] = 700
        if node.has_label('RULE'):
            data['name'] = property['ruleName']
        for key, value in property.items():
            if key == 'name':
                value = value.split('_')[0]
            data[key] = value
    response = {
        "data": data,
        "group" : "nodes"
    }
    return response

# Node 내용
def get_node(request):
    detected_rule = request['detected_rule']
    eventTime = request['eventTime']
    cloud = request['cloud']
    id = request['id']
    global graph
    cypher = f"""
    MATCH(r:RULE:{cloud} {{ruleName:'{detected_rule}'}})<-[d:DETECTED]-(l:LOG:{cloud} {{eventTime:'{eventTime}'}})<-[:ACTED|CONNECTED]-()
    WHERE ID(d) = {id}
    OPTIONAL MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*7]-()
    WITH r, d, l, p
    CALL apoc.do.when(
        p IS NULL,
        "MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*]-() WITH COLLECT(p)[-1] as p RETURN p as p",
        "MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*7]-() WITH COLLECT(p)[-1] as p RETURN p as p",
        {{r:r, d:d, l:l}}
    ) YIELD value
    WITH value,
        CASE
            WHEN l.userIdentity_type <> 'IAMUser' THEN l.userIdentity_type
            ELSE l.userIdentity_userName
        END AS name
    MATCH (a:Actor {{name: name}})
    UNWIND NODES(value.p) as nodes
    WITH COLLECT(DISTINCT(nodes)) as nodes, a as actor
    RETURN nodes, actor
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for node in data['nodes']:
            response.append(get_node_json(node, cloud))
        response.append(get_node_json(data['actor'], cloud))
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
    MATCH (r:RULE:{cloud} {{ruleName:'{detected_rule}'}})<-[d:DETECTED]-(l:LOG:{cloud} {{eventTime:'{eventTime}'}})<-[:ACTED|CONNECTED]-()
    WHERE ID(d) = {id}
    OPTIONAL MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*7]-()
    WITH r, d, l, p
    CALL apoc.do.when(
        p IS NULL,
        "MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*]-(x) WITH COLLECT(p)[-1] AS p, COLLECT(x)[-1] AS x RETURN p as p, x as x",
        "MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*7]-(x) WITH COLLECT(p)[-1] AS p, COLLECT(x)[-1] AS x RETURN p AS p, x AS x",
        {{r:r, d:d, l:l}}
    ) YIELD value
    WITH value,
        CASE
            WHEN l.userIdentity_type <> 'IAMUser' THEN l.userIdentity_type
            ELSE l.userIdentity_userName
        END AS name
    MATCH (a:Actor {{name: name}})
    CALL apoc.create.vRelationship(a, 'ACTED', {{}}, value.x) YIELD rel AS temp_rel
    UNWIND RELATIONSHIPS(value.p) as rel
    WITH DISTINCT(rel) as rel, temp_rel
    WITH
        [
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
    RETURN
        COLLECT(relation) as relations,
        temp_rel
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for relation in data['relations']:
            response.append(get_relation_json(relation))
        response.append(get_relation_json(data['temp_rel']))
    return response

# 로그 디테일
def get_log_details(request):
    detected_rule = request['detected_rule']
    eventTime = request['eventTime']
    cloud = request['cloud']
    id = request['id']
    global graph
    cypher = f"""
    MATCH(r:RULE:{cloud} {{ruleName:'{detected_rule}'}})<-[d:DETECTED]-(l:LOG:{cloud} {{eventTime:'{eventTime}'}})<-[:ACTED|CONNECTED]-()
    WHERE ID(d) = {id}
    MATCH p=(r)<-[]-(l)<-[:ACTED|DETECTED|CONNECTED*7]-(x)
    WITH r, d, l, p
    CALL apoc.do.when(
        p IS NULL,
        "MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*]-() WITH COLLECT(p)[-1] AS p RETURN p as p",
        "MATCH p=(r)<-[d]-(l)<-[:ACTED|CONNECTED*7]-() WITH COLLECT(p)[-1] AS p RETURN p AS p",
        {{r:r, d:d, l:l}}
    ) YIELD value
    UNWIND NODES(value.p) as node
    WITH DISTINCT(node) as node, l, r
    WHERE node <> r
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