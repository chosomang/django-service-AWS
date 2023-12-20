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

def get_alert_logs(request=dict):
    print(request)
    page =  1 if 'page' not in request else request['page'][0]
    order = [] if 'order' not in request else request['order']
    filter_dict = {} if 'filter' not in request else request['filter']
    limit = 1 if 'limit' not in request else request['limit']
    
    
    cypher = """
    MATCH (l:Log)-[d:DETECTED|FLOW_DETECTED]->(r:Rule)
    RETURN
        HEAD([label IN labels(r) WHERE label <> 'Rule']) AS logType,
        l.eventTime as eventTime,
        l.eventTime AS eventTime_format,
        r.ruleComment as ruleComment,
        l.eventName as eventName,
        CASE
            WHEN r.level = 1 THEN ['LOW', 'success']
            WHEN r.level = 2 THEN ['MID', 'warning']
            WHEN r.level = 3 THEN ['HIGH', 'caution']
            ELSE ['CRITICAL', 'danger']
        END AS severity,
        CASE
            WHEN l.sourceIPAddress IS NOT NULL THEN l.sourceIPAddress
            WHEN l.sourceIp IS NOT NULL THEN l.sourceIp
            ELSE '-'
        END AS sourceIp,
        r.ruleName as detected_rule,
        r.ruleClass as rule_class,
        r.ruleName+'#'+id(d) AS rule_name,
        ID(d) as id,
        CASE
            WHEN d.alert <> 1 THEN 0
            WHEN d.alert IS NULL THEN 0
            ELSE 1
        END AS alert
    ORDER BY alert, eventTime DESC, r.level DESC
    LIMIT 10
    """
    results = graph.run(cypher)
    data = []
    filter = ['logType', 'detected_rule', 'eventTime', 'rule_name', 'alert', 'id', 'rule_class']
    for result in results:
        detail = dict(result.items())
        form = {}
        for key in filter:
            if key not in ['logType', 'rule_name', 'alert']:
                value = detail.pop(key)
            else:
                value = detail[key]
            form[key] = value
        detail['form'] = form
        data.append(detail)
    context = {'data': data}
    return context

# Filtered alerts
def get_filtered_alerts():
    cypher = """
    """
    results = graph.run(cypher)
    data = check_filtered_alerts()
    filter = ['logType', 'detected_rule', 'eventTime', 'rule_name', 'id', 'rule_class']
    for result in results:
        detail = dict(result.items())
        form = {}
        for key in filter:
            if key != 'logType' and key != 'rule_name':
                value = detail.pop(key)
            else:
                value = detail[key]
            form[key] = value
        detail['form'] = form
        data.append(detail)
    context = {'data': data}
    return context

def check_filtered_alerts():
    data = []
    return data


def get_filter_list():

    response = {}
    return response
# Top Bar 알림
def check_topbar_alert():
    cypher = """
    MATCH (r:Rule)<-[d:DETECTED|FLOW_DETECTED]-()
    WHERE d.alert = 0 OR d.alert IS NULL
    SET d.alert = CASE
            WHEN d.alert IS NULL THEN 0
            ELSE d.alert
        END
    RETURN COUNT(d) as count
    """
    count = graph.evaluate(cypher)
    if count > 0:
        response = {'top_alert':{'count': count}}
        cypher = """
        MATCH (r:Rule)<-[d:DETECTED|FLOW_DETECTED]-(l:Log)
        WHERE d.sent = 0 OR d.sent IS NULL
        WITH DISTINCT(d) as d, r, l
        SET d.sent = CASE
                WHEN d.sent IS NULL THEN 0
                ELSE d.sent
            END
        RETURN r, l, ID(d) as id_d
        """
        if graph.evaluate(cypher) is not None:
            results = graph.run(cypher)
            for result in results:
                cypher = f"""
                MATCH (r:Rule)<-[d:DETECTED|FLOW_DETECTED]-(l:Log)
                WHERE ID(r) = {result['r'].identity} AND
                    ID(l) = {result['l'].identity} AND
                    ID(d) = {result['id_d']} AND
                    (d.sent = 0 OR d.sent IS NULL)
                SET d.sent = 1
                RETURN count(d)
                """
                graph.evaluate(cypher)
                send_alert_mail(dict(result['r']), dict(result['l']), result['id_d'])
    else:
        response = {'no_top_alert': 1}
    return response

# 알림 메일
def send_alert_mail(rule, log, rel_id):
    return 1
    # subject = f"Teiren SIEM Rule Detection Alert Mail [{rule['ruleName']}#{rel_id}]"
    # message = ''
    # from_email = settings.EMAIL_HOST_USER
    # recipient_list = ['chosomang12@gmail.com']
    # context = {
    #     'r': rule,
    #     'rel_id': rel_id,
    #     'l': log,
    # }
    # html_message = render_to_string('risk/alert/mail.html', context)
    # send_mail(subject, message, from_email, recipient_list, html_message=html_message)

# 위협 알림 확인 후 Alert Off
def alert_off(request):
    if 'alert' in request:
        graph.evaluate(f"""
        MATCH (r:Rule:{request['logType']} {{ruleName:'{request['detected_rule']}'}})<-[d:DETECTED|FLOW_DETECTED]-(l:Log:{request['logType']} {{eventTime:'{request['eventTime']}'}})
        WHERE
            d.alert IS NOT NULL AND
            d.alert = 0 AND
            ID(d) = {request['id']}
        SET d.alert = 1
        RETURN count(d.alert)
        """)
    return request

