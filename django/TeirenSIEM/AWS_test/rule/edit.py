from django.conf import settings
from py2neo import Graph, ClientError
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

## Edit Rule Modal
# List Edit Rule Details (For Edit Rule Modal)
def get_edit_rule_page(request):
    rule_type = request['log_type']
    og_rule_name = request['rule_name']
    cloud = request['cloud']
    global graph
    response ={}
    if rule_type == 'FLOW':
        cypher = f"""
            MATCH (r:RULE:FLOW:{cloud} {{ruleName:'{og_rule_name}'}})
            RETURN r
        """
        results = graph.run(cypher)
        filter = ['level', 'ruleType', 'eventSource', 'ruleName', 'ruleComment', 'on_off', 'blank']
        for result in results:
            flow = dict(result['r'])
            rule = {}
            for key, value in flow.items():
                if key not in filter:
                    rule.update({key:value})
            flow.update({'rule': rule})
        flow.update({'request': request})
        response = {'flow': flow}
        cypher = f"""
            MATCH (r:RULE:{cloud})
            WHERE NOT 'FLOW' IN labels(r)
            RETURN distinct(r.ruleName) as actions
        """
        results = graph.run(cypher)
        actions = []
        for result in results:
            actions.append(result['actions'])
        response.update({'actions': actions})
    else:
        cypher = f"""
        MATCH (r:RULE:{cloud}{{ruleName:'{og_rule_name}', eventSource:'{rule_type}.amazonaws.com'}})
        RETURN
            r.ruleName as ruleName,
            r.ruleComment as ruleComment,
            r.level as level,
            r.on_off as on_off
        """
        results = graph.run(cypher)
        for result in results:
            normal = dict(result)
            break
        ## Properties
        cypher = f"""
        MATCH (r:RULE:{cloud} {{ruleName:'{og_rule_name}', eventSource:'{rule_type}.amazonaws.com'}})
        UNWIND keys(r) as key
        WITH key, r
        WHERE NOT key IN ['level', 'ruleType', 'eventSource', 'ruleName', 'ruleComment', 'on_off']
        WITH DISTINCT(key) as key, r
        return {{key:key, value:r[key]}} as properties
        """
        results = graph.run(cypher)
        properties = []
        for result in results:
            properties.append(result['properties'])
        normal.update({'properties': properties})
        normal.update({'request': request})
        cypher = f"""
        MATCH (l:LOG:{cloud})<-[:DETECTED]-()
        WITH KEYS(l) AS keys
        RETURN apoc.coll.toSet(REDUCE(res = [], k IN COLLECT(DISTINCT(keys)) | res + k)) AS property
        """
        results = graph.evaluate(cypher)
        normal.update({'log_properties': results})
        response.update({'normal': normal })
        ## Log Types
        cypher = f"""
        MATCH (l:LOG:{cloud})
        WITH DISTINCT(split(l.eventSource, '.')[0]) as eventSource
        WHERE NOT eventSource CONTAINS ',' and eventSource <> 'All'
        RETURN eventSource
        """
        results = graph.run(cypher)
        types = []
        for result in results:
            if result['eventSource'] != rule_type and result['eventSource'] != 'All':
                types.append(result['eventSource'])
    return response

# Edit Rule Action
def edit_rule(request):
    og_name = request['og_rule_name']
    cloud = request['cloud']
    is_flow = request['is_flow']
    id = request['rule_id']
    ## If not Flow Rule
    if is_flow == '0':
        global graph
        ## Rule Backup
        cypher = f"""
        MATCH (r:RULE:{cloud} {{ruleName:'{og_name}'}})
        RETURN r
        """
        backup = graph.evaluate(cypher)
        ## Rule Properties Reset
        cypher = f"""
        MATCH (r:RULE:{cloud} {{ruleName:'{og_name}'}})
        UNWIND KEYS(r) as key
        WITH r, key
        WHERE NOT key IN ['level', 'ruleType', 'eventSource', 'ruleName', 'ruleComment', 'on_off']
        WITH r, COLLECT(key) as keys
        CALL apoc.create.removeProperties(r, keys) YIELD node
        return r
        """
        graph.evaluate(cypher)
        ## Match Rule
        cypher = f"""
        MATCH (r:RULE:{cloud} {{ruleName:'{og_name}'}})
        RETURN r
        """
        node = graph.evaluate(cypher)
        filter = ['og_rule_name', 'on_off', 'cloud', 'is_flow', 'rule_id']
        ## Request Parameters
        for key, value in request.items():
            if key in filter:
                continue
            if key == 'eventSource':
                value = f"{value}.amazonaws.com"
            if key == 'ruleName':
                if value != og_name:
                    check = graph.evaluate(f"""
                        MATCH (n:RULE:{cloud} {{ruleName:'{value}'}}) 
                        RETURN COUNT(n)
                    """)
                    if check > 0:
                        return '이미 존재하는 정책 이름입니다.'
            if 'property' in key:
                if 'key' in key:
                    continue
                if 'val' not in key and 'key' not in key:
                    if value == '새로운 정책 특성':
                        if not request[f'property_key{key[-1]}']:
                            return f"새로운 정책 특성 {key[-1]}을 입력해주세요"
                        request[f'property{key[-1]}'] = request[f'property_key{key[-1]}']
                    elif '특성' in value:
                        return f"정책 특성 {key[-1]}을 선택해주세요"
                if 'val' in key:
                    if not value:
                        return f"정책 특성 값 {key[-1]}을 선택해주세요"
                    key = request[f'property{key[-1]}']
                    if key and '특성' not in key:
                        if key in node:
                            count = 1
                            for property in node:
                                if key in property:
                                    count += 1
                            key = f'{key}{count}'
                        node[key] = value
            else:
                node[key] = value
        try:
            graph.push(node)
            del node
            response = '정책 수정 성공'
        except ClientError as e:
            graph.push(backup)
            del backup
            response = '정책 수정 실패'
    else:
        ## Rule Backup
        cypher = f"""
            MATCH (r:RULE:FLOW:{cloud} {{ruleName:'{og_name}'}})
            WHERE id(r) = {int(id)}
            RETURN r
        """
        backup = graph.evaluate(cypher)
        ## Rule Properties Reset
        cypher = f"""
        MATCH (r:RULE:{cloud} {{ruleName:'{og_name}'}})
        UNWIND KEYS(r) as key
        WITH r, key
        WHERE NOT key IN ['level', 'ruleType', 'eventSource', 'ruleName', 'ruleComment', 'on_off', 'blank']
        WITH r, COLLECT(key) as keys
        CALL apoc.create.removeProperties(r, keys) YIELD node
        return r
        """
        graph.evaluate(cypher)
        ## Match Rule
        cypher = f"""
            MATCH (r:RULE:FLOW:{cloud} {{ruleName:'{og_name}'}})
            WHERE id(r) = {int(id)}
            RETURN r
        """
        node = graph.evaluate(cypher)
        eventSource = ''
        rules = []
        filters = ['og', 'cloud', 'is_flow', 'rule_id']
        for key, value in request.items():
            if any(key.startswith(filter) for filter in filters):
                continue
            if key == 'ruleName':
                if value != og_name:
                    check = graph.evaluate(f"""
                        MATCH (n:RULE:{cloud} {{ruleName:'{value}'}}) 
                        RETURN COUNT(n)
                    """)
                    if check > 0:
                        return '이미 존재하는 정책 이름입니다.'
            if key == f"rule{key[-1]}":
                if value:
                    cypher = f"""
                    MATCH (r:RULE:{cloud} {{ruleName: '{value}'}})
                    RETURN r.eventSource as eventSource
                    """
                    source = graph.evaluate(cypher)
                    eventSource += f'{source}, '
                    rules.append(value)
            else:
                node[key] = value
        if len(rules) < 2:
            return "정책 행위를 추가해주세요"
        for i,(rule) in enumerate(rules, start =1):
            node[f"rule{i}"] = rule
        node['eventSource'] = eventSource[0:-2]
        try:
            graph.push(node)
            del node
            response = '정책 수정 성공'
        except ClientError as e:
            graph.push(backup)
            del backup
            response = '정책 수정 실패'
    return response

# Add Action in Edit Rule Modal
def edit_rule_add_action(request):
    cloud = request['cloud']
    count = int(request['count']) +1
    global graph
    cypher = f"""
    MATCH (r:RULE:{cloud})
    WHERE NOT 'FLOW' IN labels(r)
    WITH distinct(r.ruleName) as actions
    RETURN COLLECT(actions) as actions
    """
    results = graph.run(cypher)
    for result in results:
        actions = result
    response = {'count': count, 'actions': actions[0]}
    return response

# Change Epoch To Time
def timerange_to_timedict(timerange):
    time = int(timerange / 1000)
    seconds = int(time)
    minutes = int(seconds/60)
    hours = int(minutes/60)
    days = int(hours/24)
    seconds = int(seconds % 60)
    minutes = int(minutes % 60)
    hours = int(hours % 24)
    response = {
        'seconds': seconds,
        'minutes': minutes,
        'hours': hours,
        'days': days
    }
    return response

# Change Time to Epoch
def timedict_to_timerange(time):
    days = int(time['days']) if 'days' in time else 0
    hours = int(time['hours']) if 'hours' in time else 0
    minutes = int(time['minutes']) if 'minutes' in time else 0
    seconds = int(time['seconds']) if 'seconds' in time else 0
    days *= 86400
    hours *= 3600
    minutes*= 60
    result = days+hours+minutes+seconds
    result *= 1000
    response = result
    return response