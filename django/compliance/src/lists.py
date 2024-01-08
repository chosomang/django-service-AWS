from django.conf import settings
from py2neo import Graph
# import json
from datetime import datetime  # Add this import for timestamp
from ..models import Document

## Graph DB 연동
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:7688", auth=(username, password))

def get_lists_version(compliance_type, data=None):
    where_version = ''
    where_product = ''
    if data:
        version = data['version']
        product = data['product']
        if compliance_type == 'Isms_p':
            where_version = f"WHERE i.date = date('{version}')"
            where_product = f"WHERE p.name = '{product}'"
        else:
            where_version = f"WHERE v.date = date('{version}')"
    if compliance_type == 'Isms_p':
        results = graph.run(f"""
        MATCH (i:Compliance:Version{{name:'{compliance_type}'}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article)
        {where_version if where_version else ''}
        OPTIONAL MATCH (m)<-[r:COMPLY]-(p:Product:Evidence:Compliance)
        {where_product if where_product else ''}
        WITH split(m.no, '.') as articleNo, c, n, m, coalesce(r, {{score: 0}}) as r, p
        WITH toInteger(articleNo[0]) AS part1, toInteger(articleNo[1]) AS part2, toInteger(articleNo[2]) AS part3, c, n, m, r, p
        RETURN
            c.no as chapterNo,
            c.name as chapterName,
            n.no as sectionNo,
            n.name as sectionName,
            m.no as articleNo,
            m.name as articleName,
            m.comment as articleComment,
            r.score as complyScore
        ORDER BY part1, part2, part3
        """)
    else:
        # 법령은 PRODUCT 가 필요없을 수도 있다? -- 성연과 상의 (법령은 증적을 수집하는게 아니다/product별로 법령은 지키는 것을 보여줄 필요는 없다)
        results = graph.run(f"""
        OPTIONAL MATCH (l:Law{{name:'{compliance_type}'}})-[:VERSION]->(v:Version)-[*]->(a:Article)
        {where_version if where_version else ''}
        WITH l, v, a
        OPTIONAL MATCH (v)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a)
        WITH l, v, c, a, s
        OPTIONAL MATCH (v)-[:CHAPTER]->(c1:Chapter)-[:ARTICLE]->(a)
        WITH
            l, v, c, a, s, c1,
            toInteger(COALESCE(c.no, 0)) + toInteger(COALESCE(c1.no, 0)) as chapterOrder,
            toInteger(a.no) as articleOrder,
            toInteger(s.no) as sectionOrder
        RETURN
            COALESCE(l.name, '') AS lawName,
            COALESCE(COALESCE(c.no + '장', '') + COALESCE(c1.no + '장', ''), '') AS chapterNo,
            COALESCE(COALESCE(c.name, '') + COALESCE(c1.name, ''), '') AS chapterName,
            COALESCE(s.no + '절', '') AS sectionNo,
            COALESCE(s.name, '') AS sectionName,
            COALESCE(a.no + '조', '') AS articleNo,
            COALESCE(a.name, '') AS articleName,
            a.comment AS articleComment
        ORDER BY chapterOrder, sectionOrder, articleOrder
        """)
    response = []
    for result in results:
        response.append(dict(result.items()))

    if data:
        return response
    else:
        version_list = graph.evaluate(f"""
            MATCH (n:Compliance:Version{{name:'{compliance_type}'}})       
            return COLLECT(n.date)
        """)

        results = graph.run(f"""
        MATCH (e:Evidence:Compliance{{name:'Evidence'}})-[:PRODUCT]->(p:Evidence:Compliance:Product)
        RETURN
            p.name as productName
            order by productName
        """)
        resource_list = []
        for result in results:
            resource_list.append(dict(result.items()))
        
        return {'compliance': response,
                'version_list': version_list,
                'resource_list': resource_list}


def modify_lists_comply(compliance_type, data):
    version = data['version']
    product = data['product']
    article = data['article']
    score = data['value']

    if score  == '0':
        try:
            graph.evaluate(f"""
            MATCH (i:Compliance:Version{{name:'{compliance_type}', date:date('{version}')}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article{{no:'{article}'}})<-[r:COMPLY]-(p:Product:Evidence:Compliance{{name:'{product}'}})
            detach delete r
            return 0 as score
            """)
            return "Success"
        except:
            return "Fail"
    elif 1 <= int(score) <= 2:
        try:
            if 2 >= graph.evaluate(f"""
            MATCH (i:Compliance:Version{{name:'{compliance_type}', date:date('{version}')}})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->(n:Certification:Compliance:Section)-[:ARTICLE]->(m:Certification:Compliance:Article{{no:'{article}'}})
            OPTIONAL MATCH (m)<-[r:COMPLY]-(p:Product:Evidence:Compliance{{name:'{product}'}})
            with i, m, p, r
            call apoc.do.when (r is null,
            'match (pro:Product:Evidence:Compliance{{name:"{product}"}}) merge (m)<-[re:COMPLY{{score:{score}}}]-(pro) return re.score as score',
            'set r.score = {score} return r.score as score',
            {{r:r, p:p, m:m, i:i}})
            yield value
            return value.score as score
            """) >= 1 :
                return "Success"
            else:
                raise Exception
        except Exception:
            return "Fail"
    else:
        return "Fail"
        

def get_lists_details(compliance_type, data):
    no = data['no']

    results  = graph.run(f"""
    OPTIONAL MATCH (l:Law)-[:VERSION]->(v:Version)-[*]->(a:Article)<-[:MAPPED]->(i:Certification{{no:'{no}'}})
    WITH l, v, a, i
    OPTIONAL MATCH (v)-[:CHAPTER]->(c:Chapter)-[:SECTION]->(s:Section)-[:ARTICLE]->(a)<-[:MAPPED]->(i)
    WITH l, v, c, a, i, s
    OPTIONAL MATCH (v)-[:CHAPTER]->(c1:Chapter)-[:ARTICLE]->(a)<-[:MAPPED]->(i)
    RETURN
    COALESCE(l.name, '') AS lawName,
    COALESCE(COALESCE(c.no + '장', '') + COALESCE(c1.no + '장', ''), '') AS chapterNo,
    COALESCE(COALESCE(c.name, '') + COALESCE(c1.name, ''), '') AS chapterName,
    COALESCE(s.no + '절', '') AS sectionNo,
    COALESCE(s.name, '') AS sectionName,
    COALESCE(a.no + '조', '') AS articleNo,
    COALESCE(a.name, '') AS articleName
    ORDER BY lawName
    """)
    law = []
    for result in results:
        law.append(dict(result.items()))
    
    # query 수정 완
    results = graph.run(f"""
    MATCH (n:Certification:Compliance:Article{{compliance_name:'{compliance_type}', no:'{no}'}})
    RETURN
        n.no as articleNo,
        n.name as articleName,
        n.comment as articleComment,
        n.checklist as articleChecklist,
        n.example as articleExample
    """)
    article = []
    for result in results:
        article.append(dict(result.items()))

    #query 수정 완 
    results = graph.run(f"""
    MATCH (f:File:Compliance:Evidence)<-[:FILE]-(d:Compliance:Evidence:Data)-[:EVIDENCE]->(a:Compliance:Certification:Article{{compliance_name:'{compliance_type}', no:'{no}'}})
    RETURN
        f.name as fileName,
        f.comment as fileComment,
        f.version as fileVersion,
        f.file as dataFile,
        f.last_update as fileLastUpdate,
        f.upload_date as fileUploadDate,
        f.poc as filePoc,
        f.author as fileAuthor,
        d.name as dataName,
        d.comment as dataComment
    """)
    evidence = []
    for result in results:
        evidence.append(dict(result.items()))

    results = graph.run(f"""
    MATCH (c:Compliance:Evidence:Data)-[:EVIDENCE]->(a:Compliance:Certification:Article{{compliance_name:'{compliance_type}', no:'{no}'}})
    RETURN
        c.name as dataName,
        c.comment as dataComment,
        a.no as art_no
    """)
    category = []
    for result in results:
        category.append(dict(result.items()))
    
    return {'law': law,
            'article_list': article,
            'evidence_list' : evidence,
            'category' : category
    }

def product_data_action(request, action_type):
    if action_type == 'add':
        response = add_product_data(request)
    elif action_type == 'modify':
        response = modify_product_data(request)
    elif action_type == 'delete':
        response = delete_product_data(request)
    else:
        response = 'Fail'
    return response

def add_product_data(request):
    try:
        # Extract data from the POST request
        data = dict(request.POST.items())
        art_no = data['art_no']
        dataName = data.get('dataName', '')
        dataComment = data.get('dataComment', '')
        fileComment = data.get('fileComment', '')
        author = data.get('author', '')
        poc = data.get('poc', '')
        version = data.get('version', '')
        uploadedFile = request.FILES["uploadedFile"]

        # 디비에 파일 정보 저장
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
        MATCH (a:Compliance:Certification:Article{{compliance_name:'Isms_p', no:'{art_no}'}})
        MATCH (c:Evidence:Compliance{{name:'Evidence'}})
        MERGE (n:Compliance:Evidence:Data{{name:'{dataName}', comment:'{dataComment}'}})
        MERGE (e:Compliance:Evidence:File{{name:'{uploadedFile.name}', comment:'{fileComment}', upload_date:'{timestamp}', version:'{version}', author:'{author}', poc:'{poc}'}})
        MERGE (c)-[:DATA]->(n)
        MERGE (a)<-[:EVIDENCE]-(n)
        merge (n)-[:FILE]->(e)
        """
        # 바꿔야 됨
        """
        MATCH (p:Product:Evidence:Compliance{{name:'{AWS}'}})
        MERGE (n:Compliance:Evidence:Data{{name:'{dataName}', comment:'{dataComment}'}})
        MERGE (e:Compliance:Evidence:File{{name:'{uploadedFile.name}', comment:'{fileComment}', upload_date:'{timestamp}', version:'{version}', author:'{author}', poc:'{poc}'}})
        MERGE (p)-[:DATA]->(n)
        MERGE (a)<-[:EVIDENCE]-(n)
        MERGE (n)-[:FILE]->(e)
        """
        graph.run(add_evidence)

        response = "증적 파일이 업로드 되었습니다."
    except Exception as e:
        response = f'Error: {str(e)}'
    finally:
        return response

def modify_product_data(request):
    return 0

def delete_product_data(request):
    return 0