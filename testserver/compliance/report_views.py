# local
import os
import pytz
from datetime import datetime
from common.neo4j.handler import Neo4jHandler
from .src.report.module import convert_html_to_pdf

# django
from django.http import FileResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.shortcuts import HttpResponse

class RenderCompliance(Neo4jHandler):
    def __init__(self, request) -> None:
        super().__init__()
        self.db_name = request.session.get('db_name')
    
    def get_report_data(self):
        cypher = """
        MATCH (i:Compliance:Version{name:'Isms_p'})-[:CHAPTER]->(c:Chapter:Compliance:Certification)-[:SECTION]->
            (s:Certification:Compliance:Section)-[:ARTICLE]->(a:Certification:Compliance:Article)
        WHERE i.date = date('2023-10-31')
        OPTIONAL MATCH (a)<-[r:COMPLY]-(p:Product:Evidence:Compliance)
        WHERE p.name = 'AWS'
        OPTIONAL MATCH (a)<-[:POLICY]-(d:Data:Evidence:Compliance)<-[:DATA]-(:Policy:Evidence:Compliance)
        OPTIONAL MATCH (a)<-[:EVIDENCE]-(data:Data:Evidence:Compliance)<-[:DATA]-(p)
        OPTIONAL MATCH (a)<-[:MAPPED]->(law_a:Article)<-[*]-(law_v:Version)<-[:VERSION]-(law:Law)
        OPTIONAL MATCH (law_v)-[:CHAPTER]->(law_c:Chapter)-[:SECTION]->(law_s:Section)-[:ARTICLE]->(law_a)
        OPTIONAL MATCH (law_v)-[:CHAPTER]->(law_c1:Chapter)-[:ARTICLE]->(law_a)
        WITH split(a.no, '.') as articleNo, c, s, a, coalesce(r, {score: 0}) as r, p, i, COLLECT(d)[0] as d,
            law, law_a, law_v, law_s, law_c, law_c1
        WITH toInteger(articleNo[0]) AS part1, toInteger(articleNo[1]) AS part2, toInteger(articleNo[2]) AS part3,
            c, s, a, r, p, i, d, law, law_a, law_v, law_s, law_c, law_c1
        WITH part1, part2, part3, c, s, a, r, p, i, d,
            {
                lawname: COALESCE(law.name, ''),
                lawChapterNo: COALESCE(COALESCE(law_c.no + '장', '') + COALESCE(law_c1.no + '장', ''), ''),
                lawChapterName: COALESCE(COALESCE(law_c.name, '') + COALESCE(law_c1.name, ''), ''),
                lawSectionNo: COALESCE(law_s.no + '절', ''),
                lawSectionName: COALESCE(law_s.name, ''),
                lawArticleNo: COALESCE(law_a.no + '조', ''),
                lawArticleName: COALESCE(law_a.name, '')
            } AS law
        WITH part1, part2, part3, c, s, a, r, p, i, d, COLLECT(law) as law
        RETURN
            c.no AS chapterNo,
            c.name AS chapterName,
            s.no AS sectionNo,
            s.name AS sectionName,
            a.no AS articleNo,
            a.name AS articleName,
            a.comment AS articleComment,
            a.checklist AS articleChecklist,
            r.score AS complyScore,
            i.date AS version,
            law
        ORDER BY part1, part2, part3
        """
        results = self.run_data(database=self.db_name, query=cypher)
        
        # for result in results:
        #     # send to make_html_to_data()
        #     yield result
        
        return results
    
def make_html_to_data(request, results):
    context = {
        'page': [1, 2],
        'results': results
    }
    return render(request, f"report/index.html", context)

def make_compliance_file_name(compliance_type):
    KTZ = pytz.timezone('Asia/Seoul')
    kr_time = datetime.now(KTZ)

    return f"[Teiren] {compliance_type} Compliance Report-{kr_time.strftime('%y%m%d_%H%M')}.pdf"
        
@login_required
def report(request, compliance_type):
    user_uuid = request.session.get('uuid')
    file_name = make_compliance_file_name(compliance_type)
    compliance_folder_path = f"{settings.MEDIA_ROOT}{user_uuid}/compliance-report"
    compliance_file_path = f"{compliance_folder_path}/{file_name}"
    
    try:
        os.mkdir(f'{compliance_folder_path}')
    except FileExistsError:
        pass
    except Exception as e:
        print(e)
        os.mkdir('Error')
        user_uuid += '/Error'
    
    with RenderCompliance(request=request) as comphandler:
        results:list = comphandler.get_report_data()
    context = {
        'page': [1,2],
        'results': results
    }
    # settings.MEDIA_URL: /home/yoonan/webAPP/DATABASE/
    html_content =  render_to_string('report/index.html', context=context)
    result = convert_html_to_pdf(html_content=html_content, pdf_path=compliance_file_path)
    if not result:
        return HttpResponse("Error: Fail to Export Compliance PDF File")
    if os.path.exists(compliance_folder_path+'/'):
        return FileResponse(open(compliance_file_path, 'rb'), as_attachment=True, filename=file_name)
    else:
        return HttpResponse("Error: User Database Not Found")
