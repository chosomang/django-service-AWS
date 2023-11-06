import json
from pathlib import Path
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from py2neo import Graph
from django.template.loader import render_to_string
from M_threatD.src.notification.detection import get_node_json, get_relation_json
import requests
# LOCAL
# graph = Graph("bolt://127.0.0.1:7687", auth=('neo4j', 'teiren001'))

# NCP
# host = settings.NEO4J_HOST
# port = settings.NEO4J_PORT
# password = settings.NEO4J_PASSWORD
# username = settings.NEO4J_USERNAME

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / 'staticfiles'

# Create your tests here.


def main_test(request):
    cloud = "Aws"
    cypher = f"""
    match (rule:Rule {{ruleName:'test'}})<-[detect:DETECTED]-(log:Log {{eventName: 'GetCostForecast'}})
where id(detect) = 241549
WITH rule, detect, log
OPTIONAL MATCH p=(log)<-[:ACTED*6]-(:Log)
CALL apoc.do.when(
        p IS NULL,
        "
            MATCH p=(log)<-[:ACTED|DATE*]-(:Account)
            WITH COLLECT(p)[-1] as p
            WITH NODES(p) as nodes, RELATIONSHIPS(p) as relations
            RETURN nodes, relations
            ",
        "
            MATCH p=(log)<-[:ACTED*..5]-(view:Log)
            WITH COLLECT(p)[-1] as p
            WITH NODES(p) as nodes, RELATIONSHIPS(p) as relations
            WITH nodes, relations, nodes[-1] as last
            MATCH (last)<-[:ACTED*]-(date:Date)<-[date_rel:DATE]-(account:Account)
            WITH nodes + [account] as nodes, relations + [date_rel] as relations, date, last
            MATCH (last)<-[:ACTED*]-(mid:Log)
            WITH mid.eventName as eventName, COUNT(mid) as cnt, last, date, nodes, relations
            WITH apoc.map.fromPairs(COLLECT([eventName, cnt])) as prop, nodes, relations, date, last, SUM(cnt) as total
            CALL apoc.create.vNode(['Between'], apoc.map.merge(prop,{{name: total}})) YIELD node AS analysis
            CALL apoc.create.vRelationship(date,'BETWEEN',{{}}, analysis) YIELD rel AS analyze1
            CALL apoc.create.vRelationship(analysis,'BETWEEN',{{}}, last) YIELD rel AS analyze2
            WITH nodes + [date,analysis] as nodes, relations + [analyze1,analyze2] as relations
            RETURN nodes, relations
        ",
        {{log:log}}
    ) YIELD value
    WITH value.nodes + [rule] as nodes, value.relations + [detect] as relations, log
    OPTIONAL MATCH (log)-[assumed:ASSUMED]->(role:Role)
    WITH
        CASE
            WHEN role IS NULL THEN nodes
            ELSE nodes + [role]
        END AS nodes,
        CASE
            WHEN assumed IS NULL THEN relations
            ELSE relations + [assumed]
        END AS relations
    UNWIND relations as relation
    WITH nodes,
        [
            PROPERTIES(relation),
            ID(relation),
            ID(STARTNODE(relation)),
            ID(ENDNODE(relation)),
            TYPE(relation)
        ] AS relation
    RETURN nodes, COLLECT(relation) as relations
    """
    results = graph.run(cypher)
    response = []
    for result in results:
        data = dict(result)
        for node in data['nodes']:
            response.append(get_node_json(node, cloud))
        for relation in data['relations']:
            response.append(get_relation_json(relation))
    context = {'test': response}       

    return render(request, 'testing/test.html', context)

def test2(request):
    return render(request, 'testing/ajaxTesting.html')
# def cyto(request):
#     global graph
#     cypher = '''
#     MATCH (l:LOG)-[re:DETECTED|FLOW_DETECTED]->(r:RULE{is_allow:1})
#     RETURN
#         id(l) as id,
#         head([label IN labels(l) WHERE label <> 'LOG']) AS cloud,
#         apoc.date.format(re.detected_time,'ms', 'yyyy-MM-dd HH:mm:ss', 'Asia/Seoul') AS detected_time,
#         r.comment as detectedAction,
#         l.actionDisplayName as actionDisplayName,
#         l.actionResultType as actionResultType,
#         l.eventTime as eventTime,
#         apoc.date.format(l.eventTime,'ms', 'yyyy-MM-dd HH:mm:ss', 'Asia/Seoul') AS eventTime_format,
#         l.sourceIp as sourceIp,
#         r.name as detected_rule
#     ORDER BY l.eventTime DESC
#     '''
#     results = graph.run(cypher)
#     data = []
#     filter = ['cloud', 'detected_rule', 'eventTime']
#     rule_number = {}
#     for result in results:
#         detail = dict(result.items())
#         form = {}
#         for key in filter:
#             if key != 'cloud':
#                 value = detail.pop(key)
#             else:
#                 value = detail[key]
#             form[key] = value
#             if key == 'detected_rule':
#                 if value in rule_number.keys():
#                     rule_number[value] += 1
#                 else:
#                     rule_number[value] = 1
#                 detail['rule_name'] = value+'#'+str(rule_number[value])
#                 form['rule_name'] = value+'#'+str(rule_number[value])
#         detail['form'] = form
#         data.append(detail)
#     context = {'data': data}
#     return render(request, 'wish/neo4j.html', context)


# def ajax_src(request):
#     if request.method == 'POST':
#         response = json.dumps({"w": '', "h": '', "content":"""
#         <div id="recentCollectedOverview" class="mb-1 pl-1 h-100">
#     <div class="card shadow h-100 w-100">
#         <!-- Card Header - Dropdown -->
#         <div class="card-header">
#             <div class="h6 m-0 font-weight-bold text-primary">최근 수집 로그 Overview</div>
#         </div>
#         <!-- Card Body -->
#         <div class="card-body pl-0 pb-0">
#             <div class="chart-area" style="height:100%;">
#                 <canvas id="recentOverview"></canvas>
#             </div>
#         </div>
#     </div>
# </div>
# <script src="/staticfiles/js/dashboard/recentOverview.js"></script>
# <script>
#     {"Month": ["2022/12", "2023/1", "2023/2", "2023/3", "2023/4", "2023/5", "2023/6", "2023/7", "2023/8", "2023/9"], "collected_month": [0, 0, 0, 0, 0, 11179, 116862, 3952, 137, 0]}
# </script>
# """})
#         return HttpResponse(response)

# # def ajax_dst(request):
# #     if request.method == 'POST':
# #         layouts = GridLayout.objects.filter(name=request.POST['name'])
# #         for layout in layouts:
# #             items = json.loads(layout.data)
# #         for item in items:
# #             item['content'] = render_to_string(f"dashboard/items/{item['id']}.html")
# #         response = json.dumps(items)
# #         return HttpResponse(response)

# def ajax_js(request):
#     if request.method == 'POST':
#         data = request.POST.get('test')
#     else:
#         data = 'js fail'
#     return HttpResponse(data)

# def backup(request):
#     context = detection.log.backup()
#     return render(request, 'wish/test.html', context)