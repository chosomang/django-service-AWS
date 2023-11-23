from py2neo import Graph
from django.conf import settings

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))


def aws_check(request, logType):
    import boto3
    if request.method == 'POST':
        data = {}
        access_key = request.POST['access_key'].encode('utf-8').decode('iso-8859-1')  # 한글 입력 시 에러 발생 방지
        if access_key == '':
            data['class'] = 'btn btn-danger'
            data['value'] = 'Insert ACCESS KEY'
            return data
        secret_key = request.POST['secret_key'].encode('utf-8').decode('iso-8859-1')  # 한글 입력 시 에러 발생 방지
        if secret_key == '':
            data['class'] = 'btn btn-danger'
            data['value'] = 'Insert SECRET KEY'
            return data
        region_name = request.POST['region_name'].encode('utf-8').decode('iso-8859-1')
        if region_name == '':
            data['class'] = 'btn btn-danger'
            data['value'] = 'Insert REGION NAME'
            return data
        group_name = request.POST['group_name'].encode('utf-8').decode('iso-8859-1')
        if group_name == '':
            data['class'] = 'btn btn-danger'
            data['value'] = 'Insert LOG GROUP NAME'
            return data
        cypher = f"""
        MATCH (i:Integration)
        WHERE i.integrationType = 'Aws'
            AND i.accessKey = '{access_key}'
            AND i.secretKey = '{secret_key}'
            AND i.regionName = '{region_name}'
            AND i.groupName = '{group_name}'
        RETURN count(i)
        """
        if graph.evaluate(cypher) > 0 :
            data['class'] = 'btn btn-warning'
            data['value'] = 'Already Registered Information'
        else:
            client = boto3.client(
                f"{logType.lower() if logType == 'cloudtrail' else 'logs'}",
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key,
                region_name=region_name
            )
            try:
                functionName = globals()[f"{group_name if group_name =='cloudtrail' else 'cloudwatch'}_check"]
                functionName(client, group_name)
                data['class'] = 'btn btn-success'
                data['value'] = ' ✓ Verified!'
                data['modal'] = {}
                data['modal']['access_key'] = access_key
                data['modal']['secret_key'] = secret_key
                data['modal']['region_name'] = region_name
                data['modal']['group_name'] = group_name
            except Exception:
                data['class'] = 'btn btn-danger'
                data['value'] = 'Failed To Verify (Try Again)'
            finally:
                return data
        return data
    data = {}
    data['class'] = 'btn btn-danger'
    data['value'] = 'Failed To Verify (Try Again)'
    return data

def cloudtrail_check(client, group_name):
    client.lookup_events()

def cloudwatch_check(client, group_name):
    client.filter_log_events(
        logGroupName= group_name,
        limit = 1
    )