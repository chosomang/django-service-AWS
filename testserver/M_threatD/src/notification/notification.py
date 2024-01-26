# local
from common.neo4j.handler import Neo4jHandler
# django
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

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

class Notification(Neo4jHandler):
    def __init__(self, request) -> None:
        super().__init__()
        self.request = dict(request.POST.items()) if request.method == 'POST' else dict(request.GET.items())
        self.user_db = request.session.get('db_name')

    def get_alert_logs(self):
        cypher = '''
        MATCH (l:Log)-[d:DETECTED|FLOW_DETECTED]->(r:Rule)
        WHERE
            d.alert = 1 AND d.alert IS NOT NULL
        RETURN
            HEAD([label IN labels(r) WHERE label <> 'Rule']) AS logType,
            l.eventTime as eventTime,
            l.eventTime AS eventTime_format,
            r.ruleComment as detectedAction,
            l.eventName as actionDisplayName,
            CASE
                WHEN r.level = 1 THEN ['LOW', 'success']
                WHEN r.level = 2 THEN ['MID', 'warning']
                WHEN r.level = 3 THEN ['HIGH', 'caution']
                ELSE ['CRITICAL', 'danger']
            END AS level,
            CASE
                WHEN l.sourceIPAddress IS NOT NULL THEN l.sourceIPAddress
                WHEN l.sourceIp IS NOT NULL THEN l.sourceIp
                ELSE '-'
            END AS sourceIp,
            r.ruleName as detected_rule,
            r.ruleClass as rule_class,
            r.ruleName+'#'+id(d) AS rule_name,
            ID(d) as id
        ORDER BY eventTime DESC, r.level DESC
        '''
        results = self.run_data(database=self.user_db, query=cypher)
        data = self.check_alert_logs()
        filter = ['logType', 'detected_rule', 'eventTime', 'rule_name', 'id', 'rule_class']
        for result in results:
            form = {}
            for key in filter:
                if key != 'logType' and key != 'rule_name':
                    value = result.pop(key)
                else:
                    value = result[key]
                form[key] = value
            result['form'] = form
            data.append(result)
        context = {'data': data}
        return context

    def check_alert_logs(self):
        cypher = """
        MATCH (l:Log)-[d:DETECTED|FLOW_DETECTED]->(r:Rule)
        WHERE
            d.alert <> 1
        RETURN
        HEAD([label IN labels(r) WHERE label <> 'Rule']) AS logType,
            l.eventTime as eventTime,
            l.eventTime AS eventTime_format,
            r.ruleComment as detectedAction,
            l.eventName as actionDisplayName,
            CASE
                WHEN r.level = 1 THEN ['LOW', 'success']
                WHEN r.level = 2 THEN ['MID', 'warning']
                WHEN r.level = 3 THEN ['HIGH', 'caution']
                ELSE ['CRITICAL', 'danger']
            END AS level,
            CASE
                WHEN l.sourceIPAddress IS NOT NULL THEN l.sourceIPAddress
                WHEN l.sourceIp IS NOT NULL THEN l.sourceIp
                ELSE '-'
            END AS sourceIp,
            r.ruleName as detected_rule,
            r.ruleClass as rule_class,
            r.ruleName+'#'+id(d) AS rule_name,
            ID(d) as id,
            d.alert AS alert
        ORDER BY alert, eventTime DESC, r.level DESC
        """
        results = self.run_data(database=self.user_db, query=cypher)
        data = []
        filter = ['logType', 'detected_rule', 'eventTime', 'rule_name', 'alert', 'id', 'rule_class']
        for result in results:
            detail = dict(result.items())
            form = {}
            for key in filter:
                if key != 'logType' and key != 'rule_name' and key != 'alert':
                    value = detail.pop(key)
                else:
                    value = detail[key]
                form[key] = value
            detail['form'] = form
            data.append(detail)
        return data

    # Top Bar 알림
    def check_topbar_alert(self):
        cypher = """
        MATCH (r:Rule)<-[d:DETECTED|FLOW_DETECTED]-()
        WHERE d.alert = 0 OR d.alert IS NULL
        SET d.alert = CASE
                WHEN d.alert IS NULL THEN 0
                ELSE d.alert
            END
        RETURN COUNT(d) as count
        """
        result = self.run(database=self.user_db, query=cypher)
        if result['count'] > 0:
            response = {'top_alert':{'count': result['count']}}
            
            cypher = """
            MATCH (r:Rule)<-[d:DETECTED|FLOW_DETECTED]-(l:Log)
            WHERE d.sent = 0 OR d.sent IS NULL
            WITH DISTINCT(d) as d, r, l
            SET d.sent = CASE
                    WHEN d.sent IS NULL THEN 0
                    ELSE d.sent
                END
            RETURN r AS r, l AS l, ID(d) AS id_d
            """
            results = self.run_data(database=self.user_db, query=cypher)
            
            if results:
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
                    self.run(database=self.user_db, query=cypher)
                    self.send_alert_mail(dict(result['r']), dict(result['l']), result['id_d'])
        else:
            response = {'no_top_alert': 1}
        return response

    # 알림 메일
    def send_alert_mail(self, rule, log, rel_id):
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
    def alert_off(self):
        if 'alert' in self.request:
            detected_rule = self.request['detected_rule']
            logType = self.request['logType']
            eventTime = self.request['eventTime']
            id_ = self.request['id']
            cypher = f"""
            MATCH (r:Rule:{logType} {{ruleName:'{detected_rule}'}})<-[d:DETECTED|FLOW_DETECTED]-(l:Log:{logType} {{eventTime:'{eventTime}'}})
            WHERE
                d.alert IS NOT NULL AND
                d.alert = 0 AND
                ID(d) = {id_}
            SET d.alert = 1
            RETURN count(d.alert)
            """
            try:
                self.run(database=self.user_db, query=cypher)
                return True
            except:
                return False
        return self.request

