from django.conf import settings
from py2neo import Graph
import os
from datetime import datetime
from ..models import Document

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

# Asset List
def get_asset_list(asset_type=None):
    if asset_type:
        results = graph.run(f"""
        MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data{{name:'{asset_type}'}})
        OPTIONAL MATCH (n)-[:ASSET]->(m:Evidence:Compliance:Asset)
        RETURN
            n.name as dataType,
            n.comment as dataComment,
            m.type as assetType,
            m.serial_no as assetNo,
            m.name as assetName,
            m.usage as assetUsage,
            m.data as assetData,
            m.level as assetLevel,
            m.poc as assetPoC,
            m.user as assetUser,
            m.date as assetDate,
            id(m) as assetId
        """)
        assets = []
        for result in results:
            assets.append(dict(result.items()))
            

        results = graph.run(f"""
        MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data{{name:'{asset_type}'}})
        return
            n.name as dataType,
            n.comment as dataComment
        """)
        data_list = []
        for result in results:
            data_list.append(dict(result.items()))

        return {'assets': assets, 'data_list': data_list, 'asset_type': asset_type}
    else:
        return get_all_asset_list()


def get_all_asset_list():
    results = graph.run(f"""
    MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data)-[:ASSET]->(m:Evidence:Compliance:Asset)
    RETURN
        n.name as dataType,
        m.type as assetType,
        m.serial_no as assetNo,
        m.name as assetName,
        m.usage as assetUsage,
        m.data as assetData,
        m.level as assetLevel,
        m.poc as assetPoC,
        m.user as assetUser,
        m.date as assetDate
    ORDER BY
        dataType asc
    """)
    assets = []
    for result in results:
        assets.append(dict(result.items()))


    data_list = graph.evaluate(f"""
        MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data)
        where n.name <> 'File'
        with n.name as dataType order by dataType asc
        RETURN
            collect(dataType) as dataType
    """)

    response = {'assets': assets, 'data_list': data_list}

    return response

def get_file_list():
    results = graph.run(f"""
    MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})-[:DATA]->(n:Evidence:Compliance:Data{{name:'File'}})
    OPTIONAL MATCH (n)-[:FILE]->(m:Evidence:Compliance:File)
    RETURN
        m.name as fileName,
        m.comment as fileComment,
        m.author as fileAuthor,
        m.poc as filePoC,
        m.version as fileVersion,
        m.upload_date as uploadDate
    """)
    response = []
    for result in results:
        response.append(dict(result.items()))

    return response

# Asset Table Action
def asset_table_action(request, action_type):
    if action_type == 'add':
        response = add_asset_table(request)
    elif action_type == 'delete':
        response = delete_asset_table(request)
    elif action_type == 'modify':
        response = modify_asset_table(request)
    return response

def add_asset_table(request):
    try:
        asset_data = request.POST['assetData']
        data_comment = request.POST['dataComment']
        graph.run(f"""
        MATCH (c:Evidence:Compliance:Product{{name:'Asset Manage'}})
        MERGE (n:Compliance:Evidence:Data{{name:'{asset_data}', comment:'{data_comment}'}})
        MERGE (c)-[:DATA]->(n)
        """)

        response = "Successfully Created Asset Table"
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return response

def delete_asset_table(request):
    data_type = request.POST['dataType']
    try:
        graph.evaluate(f"""
        MATCH (p:Compliance:Product:Evidence{{name:'Asset Manage'}})-[:DATA]->(n:Compliance:Evidence:Data{{name:'{data_type}'}})
        OPTIONAL MATCH (n)-[:ASSET]->(a:Compliance:Evidence:Asset)
        DETACH DELETE n, a
        """)
        response = "Successfully Deleted Asset Table"
    except:
        response = 'Error'
    finally:
        return response

def modify_asset_table(request):
    try:
        data_type = request.POST['dataType']
        asset_data = request.POST['assetData']
        data_comment = request.POST['dataComment']
        graph.run(f"""
        MATCH (a:Compliance:Evidence:Product{{name:'Asset Manage'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{data_type}'}})
        set d.name = '{asset_data}', d.comment = '{data_comment}'
        """)

        response = "Successfully Modified Asset Table"
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return response


# Asset File Action
def asset_file_action(request, action_type):
    if action_type == 'add':
        response = add_asset_file(request)
    elif action_type == 'delete':
        response = delete_asset_file(request)
    elif action_type == 'modify':
        response = modify_asset_file(request)
    else:
        response = 'Fail'
    return response

def add_asset_file(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        fileComment = data.get('fileComment', '')
        author = data.get('author', '')
        poc = data.get('poc', '')
        version = data.get('version', '')
        uploadedFile = request.FILES["uploadedFile"]
        # Saving the information in the database
        document = Document(
            title=fileComment,
            uploadedFile=uploadedFile
        )
        document.save()

        documents = Document.objects.all()

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uploadedFile.name = uploadedFile.name.replace(' ', '_')

        # Create or update the node with properties
        add_evidence = f"""
        MATCH (p:Product:Compliance:Evidence{{name:'Asset Manage'}})-[:DATA]->(a:Compliance:Evidence:Data{{name:'File'}})
        MERGE (e:Compliance:Evidence:File{{name:'{uploadedFile.name}', comment:'{fileComment}', upload_date:'{timestamp}', version:'{version}', author:'{author}', poc:'{poc}'}})
        merge (a)-[:FILE]->(e)
        """
        graph.run(add_evidence)

        response = "Successfully Added File"
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return response

def delete_asset_file(request):
    data = dict(request.POST.items())
    file_name = data['file_name']
    delete_evidence = f"""
    MATCH (p:Product:Compliance:Evidence{{name:'Asset Manage'}})-[:DATA]->(d:Data:Compliance:Evidence{{name:'File'}})-[:FILE]->(n:Compliance:Evidence:File{{name:'{file_name}'}})

    DETACH DELETE n
    """

    file_path = os.path.join(settings.MEDIA_ROOT, 'result', file_name)

    try:
        os.remove(file_path)
        graph.evaluate(delete_evidence)
        response = "Successfully Deleted File"
    except:
        response = 'Error'
    finally:
        return response

def modify_asset_file(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        fileName = data.get('fileName','')
        fileComment = data.get('fileComment','')
        fileAuthor = data.get('fileAuthor','')
        fileVersion = data.get('fileVersion','')
        filePoC = data.get('filePoC','')

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or update the node with properties
        add_assets = f"""
        MATCH (a:Compliance:Evidence:Product{{name:'Asset Manage'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'File'}})-[:FILE]->(n:Compliance:Evidence:File{{name:'{fileName}'}})
        SET
            n.comment = '{fileComment}',
            n.author = '{fileAuthor}',
            n.version = '{fileVersion}',
            n.poc = '{filePoC}',
            n.last_update = '{timestamp}'
        """
        graph.run(add_assets)

        response = "Successfully Modified File"
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return response

# Asset Data Action
def asset_data_action(request, action_type):
    if action_type == 'add':
        response = add_asset_data(request)
    elif action_type == 'delete':
        response = delete_asset_data(request)
    elif action_type == 'modify':
        response = modify_asset_data(request)
    else:
        response = 'Fail'
    return response

def add_asset_data(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        assetType = data.get('assetType','')
        assetName = data.get('assetName','')
        serialNo = data.get('serialNo','')
        assetUsage = data.get('assetUsage','')
        assetData = data.get('assetData','')
        assetLevel = data.get('assetLevel','')
        assetPoC = data.get('assetPoC','')
        assetUser = data.get('assetUser','')
        dataType = data.get('dataType','')

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or update the node with properties
        add_assets = f"""
        MATCH (a:Compliance:Evidence:Product{{name:'Asset Manage'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{dataType}'}})
        MERGE (n:Compliance:Evidence:Asset{{type:'{assetType}', serial_no:'{serialNo}', name:'{assetName}', usage:'{assetUsage}', data:'{assetData}', level:'{assetLevel}', poc:'{assetPoC}', user:'{assetUser}', date:'{timestamp}'}})
        MERGE (d)-[:ASSET]->(n)
        """
        graph.run(add_assets)

        response = "Successfully Added Data"
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return response

def delete_asset_data(data):

    serial_no = data.POST['serial_no']

    delete_assets = f"""
    MATCH (n:Compliance:Evidence:Asset{{serial_no:'{serial_no}'}})

    DETACH DELETE n
    """

    try:
        graph.evaluate(delete_assets)
        response = "Successfully Deleted Data"
    except:
        response = 'Error'
    finally:
        return response

def modify_asset_data(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        assetType = data.get('assetType','')
        assetName = data.get('assetName','')
        serialNo = data.get('serialNo','')
        assetUsage = data.get('assetUsage','')
        assetData = data.get('assetData','')
        assetLevel = data.get('assetLevel','')
        assetPoC = data.get('assetPoC','')
        assetUser = data.get('assetUser','')
        dataType = data.get('dataType','')
        assetId = data.get('assetId','')

        # Add current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create or update the node with properties
        add_assets = f"""
        MATCH (a:Compliance:Evidence:Product{{name:'Asset Manage'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{dataType}'}})
        MATCH (d)-[:ASSET]->(n:Compliance:Evidence:Asset)
        WHERE id(n) = {assetId}
        SET
            n.type = '{assetType}',
            n.serial_no = '{serialNo}',
            n.name = '{assetName}',
            n.usage = '{assetUsage}',
            n.data = '{assetData}',
            n.level = '{assetLevel}',
            n.poc = '{assetPoC}',
            n.user = '{assetUser}'
        """
        graph.run(add_assets)

        response = "Successfully Modified Data"
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return response