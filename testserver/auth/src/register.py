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
    for key, value in request.items():
        if not value:
            return [f"{key.replace('_',' ').title()} Is Missing.", "Please Try Again"]
    if request['user_password'] != request['password_verification']:
        return ['Password Does Not Match','Please Try Again']
    return 'check'

import uuid
def register_account(request, ip):
    user_uuid = str(uuid.uuid4())
    cypher = f"""
    MERGE (super:Super:Teiren {{name:'Teiren'}})
    WITH super
    MERGE (super)-[:SUB]->(a:Teiren:Account {{
        userName: '{request['user_name']}',
        userPassword: '{request['user_password']}',
        email: '{request['email_add']}',
        createdTime: '{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}',
        ipAddress: '{ip}',
        uuid: '{user_uuid}',
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

def get_uuid(username, password):
    cypher = f"""
    MATCH (node:Teiren:Account)
    WHERE node.userName = '{username}'
    AND node.userPassword = '{password}'
    
    RETURN node.uuid as uuid LIMIT 1
    """
    result = graph.run(cypher)
    uuid = None
    for record in result:
        uuid = record["uuid"]
        break
    
    return str(uuid) if uuid else None