from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from pathlib import Path
from pymongo import MongoClient
from django.conf import settings
from py2neo import Graph
from datetime import datetime
from django.utils import timezone
import TeirenSIEM.AWS_test as aws
import TeirenSIEM.graphdb as graphdb
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

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / 'staticfiles'

# Create your tests here.
def test(request):
    # epoch = 1676374614161
    # data = datetime.fromtimestamp(epoch/1000 + 9*3600, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    # context = {'object': data}
    global graph
    cypher = f"""
    MATCH (n:LOG:AWS)
    WHERE n.eventSource IS NOT NULL
    WITH DISTINCT(split(n.eventSource, '.')[0]) as eventSource
    RETURN COLLECT(eventSource)
    """
    # results = graph.run(cypher)
    response = graph.evaluate(cypher)
    # for result in results:
    #     response.append(dict(result))
    context = {'test': response}
    return render(request, 'wish/test.html', context)

def cyto(request):
    global graph
    cypher = '''
    MATCH (l:LOG)-[re:DETECTED|FLOW_DETECTED]->(r:RULE{is_allow:1})
    RETURN
        id(l) as id,
        head([label IN labels(l) WHERE label <> 'LOG']) AS cloud,
        apoc.date.format(re.detected_time,'ms', 'yyyy-MM-dd HH:mm:ss', 'Asia/Seoul') AS detected_time,
        r.comment as detectedAction,
        l.actionDisplayName as actionDisplayName,
        l.actionResultType as actionResultType,
        l.eventTime as eventTime,
        apoc.date.format(l.eventTime,'ms', 'yyyy-MM-dd HH:mm:ss', 'Asia/Seoul') AS eventTime_format,
        l.sourceIp as sourceIp,
        r.name as detected_rule
    ORDER BY l.eventTime DESC
    '''
    results = graph.run(cypher)
    data = []
    filter = ['cloud', 'detected_rule', 'eventTime']
    rule_number = {}
    for result in results:
        detail = dict(result.items())
        form= {}
        for key in filter:
            if key != 'cloud':
                value = detail.pop(key)
            else:
                value = detail[key]
            form[key] = value
            if key == 'detected_rule':
                if value in rule_number.keys():
                    rule_number[value] += 1
                else:
                    rule_number[value] = 1
                detail['rule_name'] = value+'#'+str(rule_number[value])
                form['rule_name'] = value+'#'+str(rule_number[value])
        detail['form'] = form
        data.append(detail)
    context = {'data': data}
    return render(request, 'wish/neo4j.html', context)
 

def ajax_src(request):
    if request.method == 'POST':
        data = {'message': str(STATIC_DIR)}
    else:
        data = {'message': 'fail'}
    return JsonResponse(data)

def ajax_dst(request):
    if request.method == 'POST':
        data = dict(request.POST.items())
        test = graphdb.neo4j_graph(data)
        data.update(test)
    else:
        data = 'fail'
    return JsonResponse(data)

def ajax_js(request):
    if request.method == 'POST':
        data = request.POST.get('test')
    else:
        data = 'js fail'
    return HttpResponse(data)
    
def backup(request):
    context = aws.log.backup()
    return render(request, 'wish/test.html', context)
