from django.conf import settings
from py2neo import Graph

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def login_account(request):
    cypher = f"""
    MATCH (a:Teiren:Account{{
        userName: '{request['user_id']}',
        userPassword: '{request['user_password']}'
    }})
    RETURN 
    """
    try:
        if 1 == graph.evaluate(f"{cypher} COUNT(a)"):
            username = graph.evaluate(f"{cypher} a.userName")
            return username, request['user_password']
        else:
            raise Exception
    except Exception:
        return 'fail', 'fail'