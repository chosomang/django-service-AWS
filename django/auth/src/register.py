from django.conf import settings
from py2neo import Graph
from datetime import datetime

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def check_account(request):
    if 0 < graph.evaluate(f"MATCH (a:Teiren:Account {{userName:'{request['user_name']}'}}) RETURN COUNT(a)"):
        return [f"[User Name: '{request['user_name']}'] Already Exists.", "Please Try Again"]
    if 0 < graph.evaluate(f"MATCH (a:Teiren:Account {{userId:'{request['user_id']}'}})RETURN COUNT(a)"):
        return [f"[User ID: '{request['user_id']}'] Already Exists.", "Please Try Again"]
    for key, value in request.items():
        if not value:
            return [f"{key.replace('_',' ').title()} Is Missing.", "Please Try Again"]
    return 'check'

def register_account(request, ip):
    cypher = f"""
    MERGE (super:Super:Teiren {{name:'Teiren'}})
    WITH super
    MERGE (super)-[:SUB]->(a:Teiren:Account {{
        userName: '{request['user_name']}',
        userId: '{request['user_id']}',
        userPassword: '{request['user_password']}',
        email: '{request['email_add']}',
        phoneNo: '{request['phone_no']}',
        createdTime: '{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}',
        ipAddress: '{ip}',
        failCount: 0
    }})
    RETURN COUNT(a)
    """
    try:
        if 1 == graph.evaluate(cypher):
            return 'success'
        else:
            raise Exception
    except Exception:
        return 'fail'
