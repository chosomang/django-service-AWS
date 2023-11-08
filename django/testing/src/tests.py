import json
from pathlib import Path
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
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

from testing.dockerHandler.handler import DockerHandler
def trigger(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            access_key = data.get('access_key')
            secret_key = data.get('secret_key')
            region_name = data.get('region_name')
        
            # 위 3가지 속성에 해당하는 노드의 "isRunning" 속성을 py2neo를 이용해서 가져오기
            pass
        
            # isRunning을 통해, 현재 로그 수집기가 동작중인지 확인
            integration_node = graph.nodes.match("Integration",
                                     accessKey=access_key,
                                     secretKey=secret_key,
                                     regionName=region_name
                                     ).first()
            is_running = integration_node["isRunning"]
            if is_running:
                result = {'message': '로그 수집기가 이미 동작중입니다.'}
                return JsonResponse(result)
            else:
                # docker hub에 main 브랜치의 이미지를 빌드시마다 항상 가져오기.
                # 현재는 고정값으로 넣어둠
                client = DockerHandler()
                logcollector_image_name = 'aws_logcollector_image_v_1.0'
                environment = {
                    'AWS_ACCESS_KEY_ID': access_key,
                    'AWS_SECRET_ACCESS_KEY': secret_key,
                    'AWS_DEFAULT_REGION': region_name
                }
                container = client.create_container(image_name=logcollector_image_name, 
                                                    environment=environment)
                # Integration 노드의 isRunning 속성을 1로 업데이트
                integration_node['isRunning'] = 1
                graph.push(integration_node)
                
                result = {'message': f'인스턴스가 성공적으로 저장되었습니다. 인스턴스 id: {container.id}'}
                return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request method')
    # docker_handler = DockerHandler()
    # client = docker_handler.client
    
    # environment = {
    #     'AWS_ACCESS_KEY_ID': 'your_access_key',
    #     'AWS_SECRET_ACCESS_KEY': 'your_secret_key',
    #     'AWS_DEFAULT_REGION': 'your_region_name'
    # }
    
    # # handling
    # client.containers.run(
    #     'image-name',
    #     detach=True,
    #     environment=environment,
    # )
    

def running_trigger(request):
    """Running trigger for python script

    Args:
        request (bool): Return message successfully running or fail
    """
    request_dict = {
        'access_key': 'test_access_key',
        'secret_key': 'test_secret_key',
        'region_name': 'test_region_name',
        'bucket_name': 'test_bucket_name'
    }
    print(request_dict)

    return render(request, 'testing/trigger.html', {'request_dict': request_dict})

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
    context = {'test': 'test'}       

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