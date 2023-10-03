import json
from pathlib import Path
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from py2neo import Graph
from django.template.loader import render_to_string
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
    cypher = """
    MATCH (n:Log:Aws)
    RETURN KEYS(n)
    """
    nodes = graph.run(cypher)
    test =[]
    for node in nodes:
        test.append(node)
    context = {'test': test}       

    return render(request, 'testing/test.html', context)

def test2(request):
    return HttpResponse('test')
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