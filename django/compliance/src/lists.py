from django.conf import settings
from py2neo import Graph
from datetime import datetime
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
    WITH f, d
    MATCH (d)<-[:DATA]-(p:Product:Compliance:Evidence)
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
        d.comment as dataComment,
        p.name as productName
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
    
    product_list = graph.evaluate(f"""
    MATCH (p:Product:Evidence:Compliance)
    WHERE NOT p.name ENDS WITH "Manage"
    WITH p.name as product ORDER BY p.name
    RETURN COLLECT(product)
    """)
    return {'law': law,
            'article_list': article,
            'evidence_list' : evidence,
            'category' : category,
            'product_list': product_list
    }

def get_product_data_list(request):
    try:
        product = request.POST.get('product', '')
        if product:
            response = graph.evaluate(f"""
            MATCH (p:Product:Evidence:Compliance {{name:'{product}'}})-[:DATA]->(d)
            WITH d.name as data ORDER BY d.name
            RETURN COLLECT(data)
            """)
        else:
            raise Exception
    except Exception as e:
        print(e)
        response = []
    finally:
        return response

def add_compliance_evidence_file(request):
    print(request.POST.dict())
    for key, value in request.POST.dict().items():
        if not value and key not in ['version', 'poc']:
            return f"Please Enter/Select {key.replace('_', ' ').title()}"
    try:
        art_no = request.POST.get('art_no', '')
        compliance = request.POST.get('compliance', '')
        data_name = request.POST.get('data_name', '')
        product = request.POST.get('product', '')
        comment = request.POST.get('comment', '')
        author = request.POST.get('author', '')
        poc = request.POST.get('poc', '')
        version = request.POST.get('version', '')
        file = request.FILES["file"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if 0 < graph.evaluate(f"""
        MATCH (e:Compliance:Evidence:File {{name: '{file.name.replace(' ', '_')}'}})
        RETURN COUNT(e)
        """):
            response = "Already Exsisting File. Please Select New File."
        else:
            graph.run(f"""
            MATCH (a:Compliance:Certification:Article{{compliance_name:'{compliance.replace('-','_').capitalize()}', no:'{art_no}'}})
            MATCH (p:Product:Evidence:Compliance{{name:'{product}'}})
            MATCH (n:Compliance:Evidence:Data{{name:'{data_name}'}})
            MERGE (e:Compliance:Evidence:File{{name:'{file.name.replace(' ', '_')}', comment:'{comment}', upload_date:'{timestamp}', last_update:'{timestamp}', version:'{version}', author:'{author}', poc:'{poc}'}})
            MERGE (p)-[:DATA]->(n)
            MERGE (a)<-[:EVIDENCE]-(n)
            MERGE (n)-[:FILE]->(e)
            """)
            # 디비에 파일 정보 저장
            document = Document(
                title=comment,
                uploadedFile=file
            )
            document.save()
            response = "Successfully Added Evidence File"
    except Exception as e:
        print(e)
        response = f'Failed To Add Evidence File. Please Try Again.'
    finally:
        return response

def modify_compliance_evidence_file(request):
    for key, value in request.POST.dict().items():
        if not value and key not in ['version', 'author', 'poc']:
            return f"Please Enter/Select {key.replace('_', ' ').title()}"
        elif not value and key in ['art_no', 'og_data_name', 'name', 'og_file_comment']:
            return "Failed To Modify Evidence File. Please Try Again"
    try:
        # Extract data from the POST request
        art_no = request.POST.get('art_no', '')
        compliance = request.POST.get('compliance', '')
        data_name = request.POST.get('data_name', '')
        og_data_name = request.POST.get('og_data_name', '')
        product = request.POST.get('product', '')
        name = request.POST.get('name', '')
        comment = request.POST.get('comment', '')
        og_comment = request.POST.get('og_comment', '')
        author = request.POST.get('author', '')
        poc = request.POST.get('poc', '')
        version = request.POST.get('version', '')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if data_name != og_data_name:
            cypher = f"""
            MATCH (a:Compliance:Certification:Article{{compliance_name:'{compliance.replace('-','_').capitalize()}', no:'{art_no}'}})
            MATCH (p:Product:Evidence:Compliance{{name:'{product}'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{data_name}'}})
            MATCH (od:Compliance:Evidence:Data{{name:'{og_data_name}'}})
            MATCH (a)<-[evidence_rel:EVIDENCE]-(od)-[file_rel:FILE]->(f:Compliance:Evidence:File{{name:'{name}', comment:'{og_comment}'}})
            MERGE (f)<-[:FILE]-(d)-[:EVIDENCE]->(a)
            DELETE evidence_rel
            DELETE file_rel
            SET f.comment = '{comment}',
                f.author = '{author}',
                f.version = '{version}',
                f.poc = '{poc}',
                f.last_update = '{timestamp}',
                od.last_update = '{timestamp}',
                d.last_update = '{timestamp}'
            """
        else:
            # Create or update the node with properties
            cypher = f"""
            MATCH (a:Compliance:Certification:Article{{compliance_name:'{compliance.replace('-','_').capitalize()}', no:'{art_no}'}})
            MATCH (p:Product:Evidence:Compliance{{name:'{product}'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{data_name}'}})
            MATCH (a)<-[:EVIDENCE]-(d)-[:FILE]->(f:Compliance:Evidence:File{{name:'{name}', comment:'{og_comment}'}})
            SET f.comment = '{comment}',
                f.author = '{author}',
                f.version = '{version}',
                f.poc = '{poc}',
                f.last_update = '{timestamp}',
                d.last_update = '{timestamp}'
            """
        graph.run(cypher)
        if og_comment != comment:
            documents = Document.objects.filter(title=f"{og_comment}")
            for document in documents:
                if document.uploadedFile.name.endswith(name.replace('[','').replace(']','')):
                    document.title = comment
                    document.save()
        response = "Successfully Modified Evidence File"
    except Exception as e:
        print(e)
        response = f'Failed To Modify Evidence File. Please Try Again.'
    finally:
        return response

def delete_compliance_evidence_file(request):
    print(request.POST.dict())
    for key, value in request.POST.dict().items():
        if not value and key not in ['version', 'author', 'poc']:
            return f"Please Enter/Select {key.replace('_', ' ').title()}"
    try:
        art_no = request.POST.get('art_no', '')
        compliance = request.POST.get('compliance', '')
        data_name = request.POST.get('data_name', '')
        product = request.POST.get('product', '')
        name = request.POST.get('name', '')
        comment = request.POST.get('comment', '')
        author = request.POST.get('author', '')
        poc = request.POST.get('poc', '')
        version = request.POST.get('version', '')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        graph.run(f"""
        MATCH (a:Compliance:Certification:Article{{compliance_name:'{compliance.replace('-','_').capitalize()}', no:'{art_no}'}})
        MATCH (p:Product:Evidence:Compliance{{name:'{product}'}})-[:DATA]->(d:Compliance:Evidence:Data{{name:'{data_name}'}})
        MATCH (a)<-[:EVIDENCE]-(d)-[:FILE]->(f:Compliance:Evidence:File{{name:'{name}', comment:'{comment}', version:'{version}', author:'{author}', poc:'{poc}'}})
        SET d.last_update = '{timestamp}'
        DETACH DELETE f
        """)
        documents = Document.objects.filter(title=comment)
        for document in documents:
            if document.uploadedFile.name.endswith(name.replace('[','').replace(']','')):
                print(document.uploadedFile.path)
                document.uploadedFile.delete(save=False)
                document.delete()
        response = "Successfully Deleted Evidence File"
    except Exception as e:
        print(e)
        response = "Failed To Delete Evidence File. Please Try Again."
    finally:
        return response