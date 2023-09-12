from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from py2neo import Graph
import math
from datetime import datetime
from django.utils import timezone

## LOCAL
# graph = Graph("bolt://127.0.0.1:7687", auth=('neo4j', 'teiren001'))

## NCP
# host = settings.NEO4J_HOST
# port = settings.NEO4J_PORT
# password = settings.NEO4J_PASSWORD
# username = settings.NEO4J_USERNAME

## AWS
host = settings.NEO4J['HOST']
# port = settings.NEO4J["PORT"]
port = 7688
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def get_log_page(request, type):
    #페이징
    try:
        if 'page' in request:
            now_page = int(request['page'])  # 페이지
        else:
            raise ValueError
    except ValueError:
        now_page = 1
    except TypeError:
        now_page = 1

    #페이지당 보여줄 로그 개수
    limit = 10
    cypher = f"""
    MATCH (n:Log:{type.capitalize()})
    WITH n
    ORDER BY n.eventTime DESC
    SKIP {(now_page-1)*limit}
    LIMIT {limit}
    RETURN
        id(n) AS id,
        apoc.date.format(apoc.date.parse(n.eventTime, "ms", "yyyy-MM-dd'T'HH:mm:ssX"), "ms", "yyyy-MM-dd HH:mm:ss") AS eventTime,
        n.eventName AS eventName,
        split(n.eventSource, '.')[0] AS eventSource,
        n.userIdentity_arn AS userarn,
        n.userIdentity_type AS userType,
        CASE
            WHEN n.userIdentity_type <> 'IAMUser' THEN n.userIdentity_type
            ELSE n.userIdentity_userName
        END AS userName,
        n.awsRegion AS awsRegion,
        split(n.responseElements_assumedRoleUser_arn, '/')[1] AS role,
        n.sourceIPAddress AS sourceIP,
        [label IN LABELS(n) WHERE NOT label IN ['Log', 'Iam', 'Ec2'] AND size(label) = 3][0] AS cloud
    """
    log_list = []
    results = graph.run(cypher)
    for result in results:
        log_list.append(dict(result))

    page_obj={'log_list': log_list}

    #총 로그 개수
    total_log = graph.evaluate(f"""
        MATCH (n:Log:{type.capitalize()})
        RETURN COUNT(n)
    """)
    total_page = math.ceil(total_log / limit)
    st_page = max(1, now_page - 5)
    ed_page = min(total_page, now_page + 5)

    if ed_page < 10:
        ed_page=10

    page_obj['has_previous'] = True if now_page > 1 else False
    page_obj['previous_page_number']=now_page-1
    page_obj['paginator'] = {'page_range': range(st_page, ed_page+1)}
    page_obj['now_page']=now_page
    page_obj['has_next'] = True if now_page < total_page else False
    page_obj['next_page_number']=now_page+1
    page_obj['paginator']['num_pages']=total_page
    
    #상품 검색
    resource_list= graph.evaluate(f"""
    MATCH (n:Log:{type.capitalize()})
    WHERE n.eventSource IS NOT NULL
    WITH DISTINCT(split(n.eventSource, '.')[0]) AS eventSource
    ORDER BY eventSource
    RETURN COLLECT(eventSource)
    """)
    
    #유저 검색
    user_list=graph.evaluate(f"""
    MATCH (n:Log:{type.capitalize()})
    WHERE n.userIdentity_type IS NOT NULL
    WITH
        CASE
            WHEN n.userIdentity_type <> 'IAMUser' THEN n.userIdentity_type
            ELSE n.userIdentity_userName
        END AS user
    WITH DISTINCT(user)
    ORDER BY user
    RETURN COLLECT(user)
    """)

    #sourceIP 검색
    sourceip_list = graph.evaluate(f"""
    MATCH (n:Log:{type.capitalize()})
    WHERE n.sourceIPAddress IS NOT NULL
    WITH DISTINCT(n.sourceIPAddress) AS sourceIP
    ORDER BY sourceIP
    RETURN COLLECT(sourceIP)
    """)

    # awsregion 검색
    region_list = graph.evaluate(f"""
    MATCH (n:Log:{type.capitalize()})
    WHERE n.awsRegion IS NOT NULL
    WITH DISTINCT(n.awsRegion) AS awsRegion
    ORDER BY awsRegion
    RETURN COLLECT(awsRegion)
    """)


    #정규표현식
    regex_list=[]
    regex_list.append('hello')

    response = {
        'page_obj': page_obj,
        'resource_list':resource_list,
        'user_list':user_list,
        'regex_list':regex_list,
        'total_log': total_log,
        'sourceip_list': sourceip_list,
        'region_list': region_list,
        'current_log': [((now_page-1)*10)+1, now_page*10]
    }
    return response


# 로그 디테일 모달
def get_log_detail_modal(request):
    id = request['id']
    cloud = request['cloud']
    global graph
    cypher = f"""
    MATCH (l:Log:{cloud})
    WHERE ID(l) = {id}
    WITH ID(l) as id, PROPERTIES(l) as details
    RETURN id, details
    """
    results = graph.run(cypher)
    response = {}
    for result in results:
        for key, value in dict(result).items():
            if key == 'details':
                value = {keys:value[keys] for keys in sorted(value.keys())}
            response[key] = value
    return response