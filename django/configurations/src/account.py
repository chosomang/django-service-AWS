from django.conf import settings
from py2neo import Graph

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def data_masking(text):
    response = ''
    if len(text) > 6:
        masking_text = text[3:-3]
        start = text[:3]
        end = text[-3:]
    else:
        masking_text = text[1:-1]
        start = text[:1]
        end = text[-1:]
    for ch in masking_text:
        if ch in ['-', '@', '.']:
            response += ch
            continue
        response += '*'
    return start+response+end


def get_account_list():
    cypher = f"""
    MATCH (a:Teiren:Account)
    RETURN
        a.userName as userName,
        a.email as email,
        a.phoneNo as phoneNo
    ORDER BY id(a) ASC
    """
    response = []
    results = graph.run(cypher)
    for result in results:
        data = dict(result)
        for key, value in data.items():
            if key != "userName":
                data[key] = data_masking(value)
        response.append(data)
    return {'account_list': response}

def add_account(request):
    if 0 < graph.evaluate(f"MATCH (a:Teiren:Account {{userName:'{request['user_name']}'}}) RETURN COUNT(a)"):
        return f"[User Name: '{request['user_name']}'] already exists. Please try different name"
    if 0 < graph.evaluate(f"MATCH (a:Teiren:Account {{userId:'{request['user_id']}'}})RETURN COUNT(a)"):
        return f"[User ID: '{request['user_id']}'] already exists. Please try different ID"
    for key, value in request.items():
        if not value:
            return f"{key.replace('_',' ').title()} Is Missing. Please Try Again."
    cypher = f"""
    MERGE (a:Teiren:Account {{
        userName:'{request['user_name']}',
        userId:'{request['user_id']}',
        userPassword:'{request['user_password']}',
        email: '{request['email_add']}',
        phoneNo: '{request['phone_no']}'
    }})
    RETURN COUNT(a)
    """
    try:
        if 1 == graph.evaluate(cypher):
            return f"Created Account Successfully"
        else:
            raise Exception
    except Exception:
        return "Failed to add account. Please try again."

def verify_account(request):
    userName = request['user_name']
    userId = request['user_id']
    userPassword = request['user_password']

    cypher = f"""
    MATCH (a:Teiren:Account {{userName:'{userName}', userId: '{userId}'}})
    RETURN
        CASE
            WHEN a.userPassword = '{userPassword}' THEN 'success'
            ELSE 'fail'
        END AS result
    """
    result = graph.run(cypher).data()
    if len(result) < 1:
        response = '[Verification Fail] Unknown Information. Please Try Again.'
    elif result[0]['result'] == 'success':
        cypher = f"""
        MATCH (a:Teiren:Account {{userName:'{userName}', userId: '{userId}'}})
        RETURN
            a.userName as userName,
            a.userId as userId,
            a.userPassword as userPassword,
            a.email as email,
            a.phoneNo as phoneNo
        """
        results = graph.run(cypher)
        for result in results:
            response = dict(result)
            break
    else:
        response = '[Verification Fail] Wrong Information. Please Try Again.'
    return response

def edit_account(request):
    if request['og_user_name'] != request['user_name']:
        if 0 < graph.evaluate(f"MATCH (a:Teiren:Account {{userName:'{request['user_name']}'}})RETURN COUNT(a)"):
            return f"User Name: {request['user_name']} already exists. Please try different name"
    if request['og_user_id'] != request['user_id']:
        if 0 < graph.evaluate(f"MATCH (a:Teiren:Account {{userId:'{request['user_id']}'}})RETURN COUNT(a)"):
            return f"User ID: {request['user_id']} already exists. Please try different ID"
    cypher = f"""
    MATCH (a:Teiren:Account {{userName:'{request['og_user_name']}'}})
    SET
        a.userName = '{request['user_name']}',
        a.userId = '{request['user_id']}',
        a.userPassword = '{request['user_password']}',
        a.email = '{request['email_add']}',
        a.phoneNo = '{request['phone_no']}'
    RETURN count(a)
    """
    try:
        if 1 == graph.evaluate(cypher):
            return 'Changed Account Successfully'
        else:
            raise Exception
    except Exception:
        return 'Failed To Edit Account. Please Try Again.'

def delete_account(request):
    for key, value in request.items():
        if not value:
            return f"[{key.replace('_', ' ').title()}] Is Missing. Please Try Again."
    cypher = f"""
    MATCH (a:Teiren:Account {{
            userName:'{request['user_name']}',
            userId:'{request['user_id']}',
            userPassword: '{request['user_password']}'
        }})
    """
    try:
        graph.evaluate(f"{cypher} DETACH DELETE a")
        if 0 == graph.evaluate(f"{cypher} RETURN COUNT(a)"):
            return "Deleted Account Successfully"
        else:
            raise Exception
    except Exception:
        return "Failed To Delete Account. Please Try Again."
