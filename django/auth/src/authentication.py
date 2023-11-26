from django.conf import settings
from py2neo import Graph
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from datetime import datetime, date

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def login_account(request, ip):
    cypher = f"""
    MATCH (a:Teiren:Account{{
        userName: '{request['user_name']}'
    }})    
    """
    try:
        if 1 == graph.evaluate(f"{cypher} RETURN COUNT(a)"):
            if 5 <= graph.evaluate(f"{cypher} RETURN a.failCount"):
                return 'fail', 'User Id Forbidden. Please Contact Administrator'
            if 1 == graph.evaluate(f"{cypher} WHERE a.userPassword = '{request['user_password']}' RETURN COUNT(a)"):
                login_success(request['user_name'], ip)
                userName = graph.evaluate(f"{cypher} RETURN a.userName")
                return userName, request['user_password']
            else:
                return login_fail(request['user_name'], ip), 'fail'
        else:
            raise Exception
    except Exception:
        return 'fail', 'Failed To Login. Please Register'

def login_success(userName, ip):
    graph.evaluate(f"""
    MATCH (a:Account:Teiren{{
        userName: '{userName}'
    }})
    SET a.failCount = 0
    WITH a
    OPTIONAL MATCH (a)-[:DATE]-(d:Date {{date:'{str(date.today())}'}})
    WITH a, d
    CALL apoc.do.when(
        d IS NULL,
        "MERGE (a)-[:DATE]->(d:Date {{date:'{str(date.today())}'}}) RETURN d",
        "MATCH (a)-[:DATE]->(d:Date {{date:'{str(date.today())}'}}) RETURN d",
        {{a:a}}
    ) YIELD value
    WITH a, value.d as d
    OPTIONAL MATCH (a)-[c:CURRENT]->(b:Log:Teiren)
    WHERE split(b.eventTime,'T')[0] = d.date
    WITH a, b, d
    OPTIONAL MATCH (a)-[c:CURRENT]->()
    DELETE c
    WITH a, b, d
    CALL apoc.do.when(
        b IS NULL,
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{userName: a.userName, eventName:'Login', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}', sourceIp:'{ip}'}})
            MERGE (d)-[:ACTED]->(l)
            RETURN a
        ",
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{userName: a.userName, eventName:'Login', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}', sourceIp:'{ip}'}})<-[:ACTED]-(b)
            RETURN a
        ",
        {{a:a, b:b, d:d}}
    ) YIELD value
    RETURN value.a.failCount
    """)
    return 0

def login_fail(userName, ip):
    failCount = graph.evaluate(f"""
    MATCH (a:Account:Teiren{{
        userName: '{userName}'
    }})
    SET a.failCount = a.failCount + 1
    WITH a
    OPTIONAL MATCH (a)-[:DATE]-(d:Date {{date:'{str(date.today())}'}})
    WITH a, d
    CALL apoc.do.when(
        d IS NULL,
        "MERGE (a)-[:DATE]->(d:Date {{date:'{str(date.today())}'}}) RETURN d",
        "MATCH (a)-[:DATE]->(d:Date {{date:'{str(date.today())}'}}) RETURN d",
        {{a:a}}
    ) YIELD value
    WITH a, value.d as d
    OPTIONAL MATCH (a)-[c:CURRENT]->(b:Log:Teiren)
    WHERE split(b.eventTime,'T')[0] = d.date
    WITH a, b, d
    OPTIONAL MATCH (a)-[c:CURRENT]->()
    DELETE c
    WITH a, b, d
    CALL apoc.do.when(
        b IS NULL,
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{userName: a.userName, eventName:'Login', eventResult: 'Fail', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}', sourceIp:'{ip}'}})
            MERGE (d)-[:ACTED]->(l)
            RETURN a
        ",
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{userName: a.userName, eventName:'Login', eventResult: 'Fail', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}', sourceIp:'{ip}'}})<-[:ACTED]-(b)
            RETURN a
        ",
        {{a:a, b:b, d:d}}
    ) YIELD value
    RETURN value.a.failCount
    """)
    return failCount

@receiver(user_logged_out)
def logout_success(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    graph.run(f"""
    MATCH (a:Account:Teiren{{
        userName: '{user.username}'
    }})
    WITH a
    OPTIONAL MATCH (a)-[:DATE]-(d:Date {{date:'{str(date.today())}'}})
    WITH a, d
    CALL apoc.do.when(
        d IS NULL,
        "MERGE (a)-[:DATE]->(d:Date {{date:'{str(date.today())}'}}) RETURN d",
        "MATCH (a)-[:DATE]->(d:Date {{date:'{str(date.today())}'}}) RETURN d",
        {{a:a}}
    ) YIELD value
    WITH a, value.d as d
    OPTIONAL MATCH (a)-[c:CURRENT]->(b:Log:Teiren)
    WHERE split(b.eventTime,'T')[0] = d.date
    WITH a, b, d
    OPTIONAL MATCH (a)-[c:CURRENT]->()
    DELETE c
    WITH a, b, d
    CALL apoc.do.when(
        b IS NULL,
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{userName: a.userName, eventName:'Logout', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}', sourceIp:'{ip}'}})
            MERGE (d)-[:ACTED]->(l)
            RETURN a",
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{userName: a.userName, eventName:'Logout', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}', sourceIp:'{ip}'}})<-[:ACTED]-(b)
            RETURN a
        ",
        {{a:a, b:b, d:d}}
    ) YIELD value
    RETURN value
    """)
    return 0

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip