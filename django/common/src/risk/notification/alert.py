from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from py2neo import Graph
import json
from datetime import date

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
    MATCH (l:Log)-[d:DETECTED|FLOW_DETECTED]->(r:Rule)
    WHERE
        d.alert = 1 AND d.alert IS NOT NULL
    RETURN
        HEAD([label IN labels(r) WHERE label <> 'Rule']) AS cloud,
        l.eventTime AS detected_time,
        r.ruleComment as detectedAction,
        l.eventName as actionDisplayName,
        l.eventType as actionResultType,
        l.eventTime as eventTime,
        l.eventTime AS eventTime_format,
        l.sourceIPAddress as sourceIp,
        r.ruleName as detected_rule,
        r.ruleClass as rule_class,
        r.ruleName+'#'+id(d) AS rule_name,
        ID(d) as id
    ORDER BY eventTime DESC
    '''
    results = graph.run(cypher)
    data = check_alert_logs()
    filter = ['cloud', 'detected_rule', 'eventTime', 'rule_name', 'id', 'rule_class']
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
    MATCH (l:Log)-[d:DETECTED|FLOW_DETECTED]->(r:Rule)
    WHERE
        d.alert <> 1
    RETURN
        HEAD([label IN labels(r) WHERE label <> 'Rule']) AS cloud,
        l.eventTime AS detected_time,
        r.ruleComment AS detectedAction,
        l.eventName AS actionDisplayName,
        l.eventType AS actionResultType,
        l.eventTime AS eventTime,
        l.eventTime AS eventTime_format,
        l.sourceIPAddress AS sourceIp,
        r.ruleName AS detected_rule,
        r.ruleName+'#'+id(d) AS rule_name,
        r.ruleClass as rule_class,
        ID(d) AS id,
        d.alert AS alert
    ORDER BY alert, eventTime DESC
    """
    results = graph.run(cypher)
    data = []
    filter = ['cloud', 'detected_rule', 'eventTime', 'rule_name', 'alert', 'id', 'rule_class']
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

# 위협 알림 확인 후 Alert Off
def alert_off(request):
    if 'alert' in request:
        detected_rule = request['detected_rule']
        cloud = request['cloud']
        eventTime = request['eventTime']
        id = request['id']
        if cloud == 'Aws':
            cypher = f"""
            MATCH (r:Rule:{cloud} {{ruleName:'{detected_rule}'}})<-[d:DETECTED|FLOW_DETECTED]-(l:Log:{cloud} {{eventTime:'{eventTime}'}})
            WHERE
                d.alert IS NOT NULL AND
                d.alert = 0 AND
                ID(d) = {id}
            SET d.alert = 1
            RETURN count(d.alert)
            """
        graph.evaluate(cypher)
    return request
