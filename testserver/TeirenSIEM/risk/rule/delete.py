from django.conf import settings
from py2neo import Graph
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


# Delete Rule Action
def delete_rule(request):
    if request['ruleClass'] == 'Dynamic':
        if isinstance(delete_check:=delete_dynamic_rule(request),str):
            return delete_check
    else:
        if isinstance(delete_check:=delete_static_rule(request),str):
            return delete_check
    return '정책 삭제 완료'

def delete_static_rule(request):
    cloud = request['cloud']
    ruleName = request['og_rule_name'] if 'og_rule_name' in request else request['rule_name']
    cypher = f"""
    MATCH (rule:Rule:{cloud} {{ruleName:'{ruleName}'}})
    DETACH DELETE rule
    """
    try:
        graph.evaluate(cypher)
        return 1
    except:
        return '정책 수정 실패. 다시 시도해주세요.'

def delete_dynamic_rule(request):
    cloud = request['cloud']
    ruleName = request['og_rule_name'] if 'og_rule_name' in request else request['rule_name']
    cypher = f"""
    MATCH (rule:Rule:{cloud} {{ruleName:'{ruleName}'}})
    UNWIND KEYS(rule) as keys
    WITH rule, keys
    WHERE keys =~ 'flow.*'
    WITH rule, rule[keys] as flowName
    MATCH (flow:Flow{{flowName:flowName}})
    WITH rule, flow
    OPTIONAL MATCH (rule)<-[:FLOW_DETECTED]-(log:Log)
    WITH rule, flow, log
    CALL apoc.do.when(
        log IS NOT NULL,
        "
            OPTIONAL MATCH (log)<-[flow_rel:FLOW*]-(:Log)
            WITH CASE WHEN flow_rel IS NULL THEN [] ELSE flow_rel END AS flow_rel
            RETURN flow_rel AS flow_rel
        ",
        "
            RETURN [] AS flow_rel
        ",
        {{log:log}}
    )YIELD value
    WITH rule, flow, value.flow_rel as flow_rels
    CALL apoc.do.when(
        SIZE(flow_rels) > 0,
        "
            UNWIND flow_rels as flow_rel
            DELETE flow_rel
        ",
        "
            RETURN 0
        ",
        {{flow_rels:flow_rels}}
    )YIELD value
    DETACH DELETE rule, flow
    """
    try:
        graph.evaluate(cypher)
        return 1
    except:
        return '정책 수정 실패. 다시 시도해주세요.'
    

