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
    rule_type = request['log_type']
    rule_name = request['rule_name']
    rule_id = request['rule_id']
    cloud = request['cloud']
    global graph
    if rule_type == 'FLOW':
        cypher = f"""
            MATCH (f:RULE:FLOW:{cloud} {{ruleName:'{rule_name}'}})
            WHERE id(f) = {int(rule_id)}
            WITH keys(f) as keys, f
            UNWIND keys as key
            WITH f, key WHERE key=~'rule[0-9]+' and key <> 'ruleType'
            MATCH(r:RULE:{cloud} {{ruleName:f[key]}})
            DETACH DELETE f
            RETURN count(f) as count
        """
        result = graph.evaluate(cypher) is not None
        if result > 0:
            return '정책 삭제 완료'
        else:
            return '정책 삭제 실패'
    else:
        flow_check = delete_flow_check(cloud, rule_name)
        if len(flow_check) > 0:
            if 'confirm' in request:
                deleted_flow = []
                for flow in flow_check:
                    cypher = f"""
                        MATCH (f:FLOW:{cloud}{{ruleName:'{flow}'}})
                        WITH keys(f) as keys, f
                        UNWIND keys as key
                        WITH f, key WHERE key=~'rule[0-9]+'
                        MATCH(r:RULE:{cloud}{{ruleName:f[key]}})
                        WHERE r.ruleName <> '{rule_name}'
                        DETACH DELETE f
                        RETURN count(f) as count
                    """
                    result = graph.evaluate(cypher)
                    if result > 0:
                        deleted_flow.append(flow)
                    else:
                        if len(deleted_flow):
                            return json.dumps(deleted_flow)+'는 삭제하였지만 다른 정책을 삭제하는데 문제가 발생했습니다.'
                        else:
                            return 'FLOW 정책 삭제 실패'
                response = json.dumps(deleted_flow)+'정책 삭제 완료. <br> 계속 삭제를 진행하겠습니다.'
            else:
                response = '정책과 관련된 FLOW 정책:<br>'+json.dumps(flow_check)+'가(이) 존재합니다.<br>FLOW 정책도 함께 삭제됩니다.'
        else:
            cypher = f"""
                MATCH (r:RULE:{cloud}{{ruleName:'{rule_name}'}})
                DETACH DELETE r
                RETURN count(r) as count
            """
            result = graph.evaluate(cypher)
            if result > 0:
                return '정책 삭제 완료'
            else:
                return '정책 삭제 실패'
    return response

# Check and Delete Flow Rule for Delete Rule Modal
def delete_flow_check(cloud,rule_name):
    global graph
    cypher = f"""
        MATCH (f:FLOW:RULE:{cloud})
        WITH keys(f) as keys, f
        UNWIND keys as key
        WITH f, key where key=~'rule[0-9]+'
        WITH f where f[key]='{rule_name}'
        RETURN f.ruleName as name
    """
    response = []
    results = graph.run(cypher)
    for result in results:
        response.append(result['name'])
    return response