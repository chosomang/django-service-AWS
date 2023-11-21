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

def login_account(request):
    cypher = f"""
    MATCH (a:Teiren:Account{{
        userId: '{request['user_id']}'
    }})    
    """
    try:
        if 1 == graph.evaluate(f"{cypher} RETURN COUNT(a)"):
            if 5 <= graph.evaluate(f"{cypher} RETURN a.failCount"):
                return 'fail', 'User Id Forbidden. Please Contact Administrator'
            if 1 == graph.evaluate(f"{cypher} WHERE a.userPassword = '{request['user_password']}' RETURN COUNT(a)"):
                login_success(request['user_id'])
                userName = graph.evaluate(f"{cypher} RETURN a.userName")
                return userName, request['user_password']
            else:
                return login_fail(request['user_id']), 'fail'
        else:
            raise Exception
    except Exception:
        return 'fail', 'Failed To Login. Please Register'

def login_success(userid):
    graph.run(f"""
    MATCH (a:Account:Teiren{{
        userId: '{userid}'
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
    DELETE c
    WITH a, b, d
    CALL apoc.do.when(
        b IS NULL,
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{eventName:'Login', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}'}})
            MERGE (d)->[:ACTED]->(l)
            RETURN l",
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{eventName:'Login', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}'}})<-[:ACTED]-(b)
            RETURN l
        ",
        {{a:a, b:b, d:d}}
    ) YIELD value
    RETURN value
    """)
    return 0

def login_fail(userid):
    failCount = graph.evaluate(f"""
    MATCH (a:Account:Teiren{{
        userId: '{userid}'
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
    DELETE c
    WITH a, b, d
    CALL apoc.do.when(
        b IS NULL,
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{eventName:'Login', eventResult: 'Fail', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}'}})
            MERGE (d)-[:ACTED]->(l)
            RETURN a
        ",
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{eventName:'Login', eventResult: 'Fail', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}'}})<-[:ACTED]-(b)
            RETURN a
        ",
        {{a:a, b:b, d:d}}
    ) YIELD value
    RETURN value.a.failCount
    """)
    return failCount

@receiver(user_logged_out)
def logout_success(sender, user, request, **kwargs):
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
    DELETE c
    WITH a, b, d
    CALL apoc.do.when(
        b IS NULL,
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{eventName:'Logout', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}'}})
            MERGE (d)-[:ACTED]->(l)
            RETURN a",
        "
            MERGE (a)-[:CURRENT]->(l:Log:Teiren{{eventName:'Logout', eventResult: 'Success', eventTime:'{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}'}})<-[:ACTED]-(b)
            RETURN a
        ",
        {{a:a, b:b, d:d}}
    ) YIELD value
    RETURN value
    """)
    return 0