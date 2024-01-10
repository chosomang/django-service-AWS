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


# data 목록 가져오기
def get_data_list(request, data_name=None):
    try:
        response=[]
        main_search_key = request.POST.get('main_search_key', '')
        main_search_value = request.POST.get('main_search_value', '')
        if data_name:
            results = graph.run(f"""
            MATCH (p:Product:Evidence:Compliance)-[:DATA]->(d:Data:Compliance:Evidence)
            WHERE p.name <> 'Asset Manage' AND p.name <> 'Policy Manage' AND d.name = '{data_name}'
            RETURN d AS data, p AS product
            """)
        elif not main_search_key or not main_search_value:
            results = graph.run(f"""
            MATCH (p:Product:Evidence:Compliance)-[:DATA]->(d:Data:Compliance:Evidence)
            WHERE p.name <> 'Asset Manage' and p.name <> 'Policy Manage'
            RETURN d AS data, p AS product
            """)
        else:
            results = graph.run(f"""
            MATCH (p:Product:Evidence:Compliance)-[:DATA]->(d:Data:Compliance:Evidence)
            WHERE p.name <> 'Asset Manage' AND p.name <> 'Policy Manage' AND toLower(d.{main_search_key}) CONTAINS toLower('{main_search_value}')
            RETURN d AS data, p AS product
            """)
        for result in results:
            response.append(result)
    except Exception as e:
        print(e)
        response = []
    finally:
        return response

def get_product_list():
    try:
        response = graph.evaluate(f"""
        MATCH (p:Product:Evidence:Compliance)
        WHERE p.name <> 'Asset Manage' AND p.name <> 'Policy Manage'
        WITH p.name as product ORDER BY p.name
        RETURN COLLECT(product)
        """)
    except Exception as e:
        response = []
    finally:
        return response

def get_compliance_list():
    try:
        response = graph.evaluate(f"""
        MATCH (:Compliance)-[:COMPLIANCE]->(c:Compliance)
        WHERE c.name <> 'Evidence'
        WITH replace(toUpper(c.name), '_', '-') as compliance ORDER BY c.name
        RETURN COLLECT(compliance)
        """)
    except Exception as e:
        response = []
    finally:
        return response

def get_compliance_version_list(request):
    try:
        compliance = request.POST.get('compliance', '').replace('-', '_').capitalize()
        response = graph.evaluate(f"""
        MATCH (:Compliance)-[:COMPLIANCE]->(c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)
        WITH toString(v.date) as version ORDER BY v.date
        RETURN COLLECT(version)
        """)
    except Exception as e:
        response = []
    finally:
        return response

def get_compliance_article_list(request):
    try:
        compliance = request.POST.get('compliance', '').replace('-', '_').capitalize()
        version = request.POST.get('version', '')
        cypher=f"""
            OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:CHAPTER]->(:Chapter)-[:SECTION]->(:Section)-[:ARTICLE]->(a:Article)
            WITH a
            WHERE a IS NOT NULL AND v.date = date('{version}')
            RETURN a.no AS no, a.name AS name

            UNION

            OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:CHAPTER]->(:Chapter)-[:ARTICLE]->(a:Article)
            WITH a
            WHERE a IS NOT NULL AND v.date = date('{version}')
            RETURN a.no AS no, a.name AS name

            UNION

            OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:ARTICLE]->(a:Article)
            WITH a
            WHERE a IS NOT NULL AND v.date = date('{version}')
            RETURN a.no AS no, a.name AS name
        """
        response = []
        results = graph.run(cypher)
        for result in results:
            response.append({'no':result['no'], 'name': result['name']})
        response = sorted(response, key=lambda x: [int(i) for i in x['no'].split('.')])
    except Exception as e:
        print(e)
        response = []
    finally:
        return response

# data 추가
def add_evidence_data(request):
    data = dict(request.POST.items())
    for key, value in data.items():
        if value == '' and key not in ['comment', 'author', ''] :
            return f"Please Enter/Select {key.title()}"
    try:
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 0 < graph.evaluate(f"""
        MATCH (c:Data:Compliance:Evidence{{
            name:'{data['name']}'
        }})
        RETURN count(c)
        """):
            response = "Data Already Exsists. Please Enter Different Name."
        else:
            if data['article'] != '':
                cypher = f"""
                MATCH (e:Compliance:Evidence{{name:'Evidence'}})-[:PRODUCT]->(p:Product:Evidence{{name:'{data['product']}'}})
                MATCH (v:Version{{name:'{data['compliance'].replace('-','_').capitalize()}', date:date('{data['version']}')}})-[*]->(a:Article{{compliance_name:'{data['compliance'].replace('-','_').capitalize()}', no:'{data['article'].split(' ')[0]}'}})
                MERGE (p)-[:DATA]->
                    (d:Data:Compliance:Evidence {{
                    name:'{data['name']}',
                    comment:'{data['comment']}',
                    author:'{data['author']}',
                    last_update:'{last_update}'
                }})-[:EVIDENCE]->(a)
                RETURN COUNT(d)
                """
            elif data['compliance'] != '':
                cypher = f"""
                MATCH (e:Compliance:Evidence{{name:'Evidence'}})-[:PRODUCT]->(p:Product:Evidence{{name:'{data['product']}'}})
                MATCH (c:Version:Compliance{{name:'{data['compliance'].replace('-','_').capitalize()}', date:date('{data['version']}')}})
                MERGE (p)-[:DATA]->
                    (d:Data:Compliance:Evidence {{
                    name:'{data['name']}',
                    comment:'{data['comment']}',
                    author:'{data['author']}',
                    last_update:'{last_update}'
                }})-[:EVIDENCE]->(c)
                RETURN COUNT(d)
                """
            else:
                raise Exception
            if 0 == graph.run(cypher):
                raise Exception
            else:
                response = "Successfully Create Data."
    except Exception as e:
        print(e)
        response = "Failed To Create Data. Please Try Again."
    finally:
        return response

def modify_evidence_data(request):
    try:
        og_name=request.POST.get('og_name', '')
        name = request.POST.get('name', '')
        if not name:
            response = "Please Enter Data Name"
        elif not og_name:
            raise Exception
        elif og_name != name and 0 < graph.evaluate(f"""
        MATCH (c:Data:Compliance:Evidence{{
            name:'{name}'
        }})
        RETURN count(c)
        """):
            response = "Data Name Already Exsists. Please Enter New Data Name."
        else:
            comment = request.POST.get('comment', '')
            author = request.POST.get('author', '')
            last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            graph.evaluate(f"""
                MATCH (d:Data:Compliance{{name:'{og_name}'}})
                SET d.name = '{name}',
                    d.comment='{comment}',
                    d.author='{author}',
                    d.last_update='{last_update}' 
                RETURN COUNT(d)
            """)
            response = "Successfully Modified Data"
    except Exception as e:
        print(e)
        response = 'Failed To Modify Data. Please Try Again.'
    finally:
        return response

def delete_evidence_data(request):
    try:
        name = request.POST.get('name', '')
        if not name:
            raise Exception
        else:
            comment = request.POST.get('comment', '')
            author = request.POST.get('author', '')
            graph.evaluate(f"""
            MATCH (d:Compliance:Evidence:Data{{name:'{name}', comment:'{comment}', author:'{author}'}})
            WITH d
            OPTIONAL MATCH (d)-[:FILE]->(f:File:Compliance:Evidence)
            WITH d, COLLECT(f) AS file_list
            FOREACH (f IN file_list| DETACH DELETE f)
            DETACH DELETE d
            RETURN count(d)
            """)
            response = "Successfully Deleted Data"
    except Exception as e:
        print(e)
        response = "Failed To Delete Data. Please Try Again."
    finally:
        return response


def get_file_list(data_name):
    try:
        response = graph.evaluate(f"""
            MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})-[:FILE]->(file:File:Compliance:Evidence)
            RETURN collect(file)
        """)
    except Exception as e:
        print(e)
        response = []
    finally:
        return response

def get_data_related_compliance(search_cate=None, search_content=None):
    try:
        response=[]
        if search_cate=="compliance":
            cypher=f"""
                MATCH (com:Compliance{{name:'{search_content}'}})-[:VERSION]->(ver:Version)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)
                RETURN com, ver, chap, sec, arti ORDER BY arti.no
            """
        elif search_cate=="evidence":
            cypher=f"""
                MATCH (version:Version:Compliance)-[:CHAPTER]->(chapter:Chapter)-[:SECTION]->(section:Section)-[:ARTICLE]->(article:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
                RETURN version, chapter, section, article ORDER BY article.no

                UNION

                MATCH (version:Version:Compliance)-[:CHAPTER]->(chapter:Chapter)-[:ARTICLE]->(article:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
                RETURN version, chapter, '' AS section, article ORDER BY article.no

                UNION

                MATCH (version:Version:Compliance)-[:ARTICLE]->(article:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
                RETURN version, '' AS chapter, '' AS section, article ORDER BY article.no

                UNION

                MATCH (version:Version:Compliance)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
                RETURN version, '' AS chapter, '' AS section, '' AS article
            """
        results = graph.run(cypher)
        for result in results:
            response.append(result)
    except Exception as e:
        print(e)
        response = []
    finally:
        return response

def add_evidence_file(request):
    for key, value in request.POST.dict().items():
            if not value:
                return f"Please Enter/Select {key.capitalize()}"
    try:
        print(request.POST.dict())
        data_name = request.POST.get('data_name','')
        uploaded_file = request.FILES.get("file")
        if 0 < graph.evaluate(f"""
        MATCH (d:Data:Evidence:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{uploaded_file.name}'}})
        RETURN count(f)
        """):
            response = "File Name Already Exsists. Please Enter New File Name."
        else:
            comment = request.POST.get('comment','')
            author = request.POST.get('author','')
            version = request.POST.get('version','')
            poc = request.POST.get('poc','')
            upload_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Saving the information in the database
            document = Document(
                title= comment,
                uploadedFile=uploaded_file
            )
            document.save()
            uploaded_file.name = uploaded_file.name.replace(' ', '_')
            
            graph.evaluate(f"""
            MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})
            MERGE (f:File:Compliance:Evidence {{
                name:'{uploaded_file.name}',
                comment:'{comment}',
                author:'{author}',
                poc:'{poc}',
                version:'{version}',
                upload_date:'{upload_date}'
            }})
            MERGE (d)-[:FILE]->(f)
            SET d.last_update='{upload_date}'
            """)
            response = "Successfully Added Evidence File"
    except Exception as e:
        print(e)
        response = 'Failed To Add Evidence File. Please Try Again.'
    finally:
        return response

def modify_evidence_file(request):
    for key, value in request.POST.dict().items():
        if not value:
            return f"Please Enter/Select {key.capitalize()}"
    try:
        data_name = request.POST.get('data_name', '')
        name = request.POST.get('name', '')
        comment = request.POST.get('comment', '')
        author = request.POST.get('author', '')
        version = request.POST.get('version', '')
        poc = request.POST.get('poc', '')
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        graph.evaluate(f"""
        MATCH (d:Data:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{name}'}})
        SET f.comment='{comment}', 
            f.author='{author}', 
            f.version='{version}',
            f.poc='{poc}',
            f.last_update='{last_update}',
            d.last_update='{last_update}'
        """)
        response = "Successfully Modified Evidence File"
    except Exception as e:
        print(e)
        response = "Failed To Modify Evidence File"
    finally:
        return response

def delete_evidence_file(request):
    print(request.POST.dict())
    try:
        data_name = request.POST.get('data_name', '')
        name = request.POST.get('name', '')
        comment = request.POST.get('comment', '')
        author = request.POST.get('author', '')
        version = request.POST.get('version', '')
        poc = request.POST.get('poc', '')
        upload_date = request.POST.get('upload_date', '')
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        graph.evaluate(f"""
        MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})-[:FILE]->
            (f:File:Evidence {{
                name:'{name}',
                comment:'{comment}',
                author:'{author}',
                poc:'{poc}',
                version:'{version}',
                upload_date: '{upload_date}'
            }})
        DETACH DELETE f
        SET d.last_update='{last_update}'
        RETURN count(f)
        """)
        response = "Successfully Deleted Evidence File"
    except Exception as e:
        print(e)
        response = "Failed To Delete Evidence File"
    finally:
        return response


#-------------------------------------------------------------------------------------------------------------------------------------------
# # 전체 컴플라이언스 리스트 가져오기 (Evidence 노드 제외)
# def get_compliance():
#     response=[]
#     cypher=f"""
#         MATCH (:Compliance)-[:COMPLIANCE]->(c:Compliance)
#         WHERE c.name <> 'Evidence'
#         RETURN c.name
#     """

#     results = graph.run(cypher)
#     for result in results:
#         response.append(result)
    
#     return response

# def get_version(dict):
#     compliance = dict['compliance_selected']

#     response=[]

#     if compliance and compliance!='none':
#         cypher=f"""
#             MATCH (:Compliance)-[:COMPLIANCE]->(c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)
#             RETURN v.date AS version
#         """
#         results = graph.run(cypher)
#         for result in results:
#             version_date = result['version'].isoformat()
#             response.append({'version': version_date})

#     return response

# # 컴플라이언스에 맞는 article 가져오기
# def get_article(dict):
#     compliance = dict['compliance_selected']
#     version=str(dict['version_selected'])
#     response=[]

#     if compliance and version and version!='none':
#         cypher=f"""
#             OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:CHAPTER]->(:Chapter)-[:SECTION]->(:Section)-[:ARTICLE]->(a:Article)
#             WITH a
#             WHERE a IS NOT NULL AND v.date = date('{version}')
#             RETURN a.no AS no, a.name AS name ORDER BY a.no

#             UNION

#             OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:CHAPTER]->(:Chapter)-[:ARTICLE]->(a:Article)
#             WITH a
#             WHERE a IS NOT NULL AND v.date = date('{version}')
#             RETURN a.no AS no, a.name AS name ORDER BY a.no

#             UNION

#             OPTIONAL MATCH (c:Compliance{{name:'{compliance}'}})-[:VERSION]->(v:Version)-[:ARTICLE]->(a:Article)
#             WITH a
#             WHERE a IS NOT NULL AND v.date = date('{version}')
#             RETURN a.no AS no, a.name AS name ORDER BY a.no
#         """

#         results = graph.run(cypher)
#         for result in results:
#             response.append({'no':result['no'], 'name': result['name']})
        
#     return response



# # file 리스트 가져오기
# def get_files(data=None):
#     if data==None:
#         return "잘못된 데이터"
#     else:
#         data=graph.evaluate(f"""
#             MATCH (d:Data:Compliance:Evidence{{name:'{data}'}})-[:FILE]->(file:File:Compliance:Evidence)
#             RETURN collect(file)
#         """)

#     return data



# def mod_file(dict):
#     data_name=dict.get('data_name', '')
#     last_name=dict.get('last_name', '')
#     name = dict.get('mod_name', '')
#     comment = dict.get('mod_comment', '')
#     author = dict.get('mod_author', '')
#     version = dict.get('mod_version', '')
#     poc = dict.get('mod_poc', '')
#     last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     if not name:
#         return 'NULL'

#     if last_name == name:
#         #data name을 수정하는 게 아니라면
#         cypher= f"""
#             MATCH (d:Data:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{last_name}'}})
#             SET f.comment='{comment}', 
#                 f.author='{author}', 
#                 f.version='{version}',
#                 f.poc='{poc}',
#                 f.last_update='{last_update}',
#                 d.last_update='{last_update}'
#             RETURN COUNT(f)
#         """
#     else:
#         #data name도 수정하는거라면 중복체크 필요
#         cypher=f"""
#             MATCH (d:Data:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{name}'}})
#             RETURN count(f)
#         """
#         if graph.evaluate(cypher) >= 1:
#             return 'already exist'

#         cypher= f"""
#             MATCH (d:Data:Compliance{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence:Compliance{{name:'{last_name}'}})
#             SET f.name='{name}',
#                 f.comment='{comment}', 
#                 f.author='{author}', 
#                 f.version='{version}',
#                 f.poc='{poc}',
#                 f.last_update='{last_update}',
#                 d.last_update='{last_update}'
#             RETURN COUNT(f)
#         """

#     try:
#         if graph.evaluate(cypher) == 1:
#             return 'success'
#         else:
#             raise Exception
#     except Exception:
#         return author
#         #return 'fail'


# # file 삭제
# def del_file(dict):
#     data_name=dict['data_name']
#     file_name=dict['file_name']
#     last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


#     cypher= f"""
#         MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})-[:FILE]->(f:File:Evidence {{name:'{file_name}'}})
#         DETACH DELETE f
#         SET d.last_update='{last_update}'
#         RETURN count(f)
#     """

#     try:
#         if 1 == graph.evaluate(cypher):
#             return 'success'
#         else:
#             raise Exception
#     except Exception:
#         return 'fail'

# def get_category_list():
#     results = graph.run("""
#     MATCH (c:Category:Compliance:Evidence)
#     RETURN
#         c.name AS name,
#         c.comment AS comment
#     """)
#     response = []
#     for result in results:
#         data = dict(result.items())
#         response.append(data)
#     return response

# def get_evidence_data(dataName):
#     try:
#         cypher = f"""
#         MATCH (c:Category:Compliance:Evidence)-[:DATA]->(d:Compliance:Data:Evidence)
#         WHERE c.name='{dataName}'
#         """
#         response = graph.run(f"{cypher} RETURN c.name AS cateName, c.comment As cateComment LIMIT 1").data()[0]
#     except:
#         response = {}
    
#     data_list=[]
#     results = graph.run(f"""{cypher}
#     RETURN
#         d.name AS name,
#         d.comment AS comment,
#         d.version_date AS version,
#         d.author AS author,
#         d.file AS file
#     """)
#     for result in results:
#         data_list.append(dict(result.items()))
    
#     law_list = []
#     results = graph.run(f"""
#     MATCH (com:Compliance)-[:VERSION]->(ver:Version)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Evidence)
#     WHERE evi.name="{dataName}"
#     RETURN 
#         com.no AS comNo,
#         com.name AS comName,
#         ver.date AS verDate,
#         chap.no AS chapNo,
#         chap.name AS chapName,
#         sec.no AS secNo,
#         sec.name AS secName,
#         arti.no AS articleNo,
#         arti.name AS articleName
#         ORDER BY arti.no
#     """)
#     for result in results:
#         law_list.append(dict(result.items()))
#     response.update({'data_list': data_list, 'law_list': law_list})
#     return response



# # 컴플라이언스와 증적 파일이 매핑된 애들을 갖고 오기
# def get_compliance_lists(search_cate=None, search_content=None):
#     response=[]
    
#     if search_cate=="com":
#         cypher=f"""
#             MATCH (com:Compliance{{name:'{search_content}'}})-[:VERSION]->(ver:Version)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)
#             RETURN com, ver, chap, sec, arti ORDER BY arti.no
#         """
#     elif search_cate=="evi":
#         cypher=f"""
#             MATCH (ver:Version:Compliance)-[:CHAPTER]->(chap:Chapter)-[:SECTION]->(sec:Section)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
#             RETURN ver, chap, secection, article ORDER BY arti.no

#             UNION

#             MATCH (ver:Version:Compliance)-[:CHAPTER]->(chap:Chapter)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
#             RETURN ver, chap, '' AS secection, article ORDER BY arti.no

#             UNION

#             MATCH (ver:Version:Compliance)-[:ARTICLE]->(arti:Article)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
#             RETURN ver, '' AS chap, '' AS secection, article ORDER BY arti.no

#             UNION

#             MATCH (ver:Version:Compliance)<-[:EVIDENCE]-(evi:Data:Compliance:Evidence{{name:'{search_content}'}})
#             RETURN ver, '' AS chap, '' AS secection, '' AS article

#         """

#     results = graph.run(cypher)
#     for result in results:
#      response.append(result)

#     return response


# # File 페이지 내 Compliance 추가
# def add_com(dict):
#     data_name = dict.get('name', '')
#     last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     compliance = dict.get('compliance', '')
#     version_selected = dict.get('version_selected', '')
#     article_selected = dict.get('article_selected', '')

#     if not version_selected or not compliance:
#         return 'NULL'       

#     #매핑 리스트가 있을 때(컴플라이언스와 관계 생성)
#     if article_selected!='none' and article_selected: 
#         #article까지 selected 했을 때
#         cypher= f"""
#                 MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})
#                 MATCH (a:Article:Compliance{{compliance_name:'{compliance}', no:'{article_selected}'}})
#                 MERGE (d)-[:EVIDENCE]->(a)
#                 SET d.last_update='{last_update}'
#                 RETURN COUNT(d)
#             """
#     elif compliance!='none': 
#     # 컴플라이언스만 selected 했을 때
#         cypher= f"""
#                 MATCH (d:Data:Compliance:Evidence{{name:'{data_name}'}})
#                 MATCH (v:Version:Compliance{{name:'{compliance}', date:date('{version_selected}')}})
#                 MERGE (d)-[:EVIDENCE]->(v)
#                 SET d.last_update='{last_update}'
#                 RETURN COUNT(d)
#             """  
#     else: 
#         return 'fail'

#     try:
#         if graph.evaluate(cypher) == 1:
#             return 'success'
#         else:
#             raise Exception
#     except Exception:
#         return 'fail'

# def add_integration(dict):
#     product = dict.get('product', '')

#     if not product:
#         return 'NULL'

#     #중복 체크 필요
#     cypher=f"""
#         MATCH (c:Product:Compliance:Evidence{{
#             name:'{product}'
#         }})
#         RETURN count(c)
#     """
#     if graph.evaluate(cypher) >= 1:
#         return 'already exist'
        
        
#     cypher= f"""
#             MATCH (e:Compliance:Evidence{{name:'Evidence'}})
#             MERGE (e)-[:PRODUCT]->
#                 (p:Product:Compliance:Evidence {{
#                 name:'{product}'
#             }})
#             RETURN COUNT(p)
#         """

#     try:
#         if graph.evaluate(cypher) == 1:
#             return 'success'
#         else:
#             raise Exception
#     except Exception:
#         return 'fail'
    
# def get_product():
#     response=[]

#     cypher=f"""
#         MATCH (product:Product:Compliance:Evidence)
#         RETURN product.name AS name ORDER BY toLower(product.name)
#     """
    
#     results = graph.run(cypher)
#     for result in results:
#         response.append(result)
    
#     return response







    



