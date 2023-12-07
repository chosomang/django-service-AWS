from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .src import evidence, lists
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os
import json
from django.http import FileResponse
from common.risk.v1.notification.alert import check_topbar_alert
from .src import evidence, lists, lists_2, version_modify, policy
from . import models


# Compliance
def compliance_view(request):
    context=' '
    return render(request, f"compliance/compliance.html", context)

# Compliance lists - 현경
def lists_view(request):

    context= lists.version()
    return render(request, f"compliance/lists.html", context)

# Compliance lists_2 - 현경
def lists_view_2(request):
    return render(request, f"compliance/lists_2.html")

def versionModify(request):
    if request.method == "POST":
        data = dict(request.POST.items())
        data.update({'compliance':version_modify.version(data)})
        return render(request, f"compliance/version_list.html", data)

# Data 리스트 출력 페이지
def data(request):
    if request.method == "GET":
        search_query1 = request.GET.get('search_query1', None)
        search_query2 = request.GET.get('search_query2', None)

        if search_query1 and search_query2:
            data_list = evidence.get_data(search_query1, search_query2)
        else:
            data_list = evidence.get_data()
        context = {'data_list': data_list}

        return render(request, "compliance/evidence/data.html", context)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)

def get_compliance(request):
    if request.method == "POST":
        compliance_list = evidence.get_compliance()
        json_data = json.dumps({"compliance_list" :compliance_list})    
        return HttpResponse(json_data, content_type='application/json')

def get_version(request):
    if request.method == "POST":
        compliance_selected=dict(request.POST.items())
        version_list = evidence.get_version(compliance_selected)
        json_data = json.dumps({"version_list" :version_list})    
        return HttpResponse(json_data, content_type='application/json')

def get_article(request):
    if request.method == "POST":
        try:
            version_selected=dict(request.POST.items())
            article_list = evidence.get_article(version_selected)
            json_data = json.dumps({"article_list" :article_list})  
            return HttpResponse(json_data, content_type='application/json')
        except Exception as e:
            # 에러가 발생한 경우
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
# Data 추가
def add_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.add_data(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
# Data 수정
def mod_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.mod_data(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    

# Data 삭제
def del_data(request):
    if request.method=="POST":
        del_data=dict(request.POST.items())

        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.del_data(del_data))   
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)

# file 출력
def get_evidence_file(request):
    if request.method == 'GET':
        # Ajax GET 요청에서 전달된 파라미터 가져오기
        title = request.GET.get('title', None)
        data=evidence.get_data('name', title)
        file_list=evidence.get_file(title)
        compliance_list=evidence.get_compliance_list('evi',title)
        
        context={
            'title':title,
            'data': data,
            'file_list': file_list,
            'compliance_list':compliance_list
        }

        if title:
            return render(request, f"compliance/evidence/file.html", context)
        else:
            # title이 없을 경우 에러 응답
            return JsonResponse({'error': 'Missing title parameter'}, status=400)
    else:
        # GET 이외의 메소드에 대한 처리
        return JsonResponse({'error': 'Invalid method'}, status=400)

# file 추가 시, 함수 동작
def add_evidence_file(request):
    add_file=dict(request.POST.items())
    return HttpResponse(evidence.add_file(add_file))

# file 수정
def mod_evidence_file(request):
    if request.method=="POST":
        mod_file=dict(request.POST.items())

        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.mod_file(mod_file))   
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
        

# file 삭제
def del_evidence_file(request):
    if request.method=="POST":
        del_file=dict(request.POST.items())
        return HttpResponse(evidence.del_file(del_file))
    
def add_com(request):
    if request.method=="POST":
        add_com=dict(request.POST.items())

        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.add_com(add_com))   
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
# Compliance lists_2 - 현경
def integration(request):
    if request.method == 'GET':
        # Ajax GET 요청에서 전달된 파라미터 가져오기
        product_list=evidence.get_product()
        
        context={
            'product_list':product_list
        }

        if product_list:
            return render(request, f"compliance/integration.html", context)
        else:
            # title이 없을 경우 에러 응답
            return JsonResponse({'error': 'Missing title parameter'}, status=400)
    else:
        # GET 이외의 메소드에 대한 처리
        return JsonResponse({'error': 'Invalid method'}, status=400)

# Data 추가
def add_integration(request):
    if request.method=="POST":
        product=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.add_integration(product))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
  
def get_product(request):
    if request.method=="POST":
        product_list = evidence.get_product()
        json_data = json.dumps({"product_list" :product_list})    
        return HttpResponse(json_data, content_type='application/json')

def get_policy(request):
    if request.method == "GET":
        search_query1 = request.GET.get('search_query1', None)
        search_query2 = request.GET.get('search_query2', None)

        if search_query1 and search_query2:
            articles_of_association=policy.get_articles_of_association(search_query1, search_query2)
            regulation=policy.get_regulation(search_query1, search_query2)
            guidelines=policy.get_guidelines(search_query1, search_query2)
            rules=policy.get_rules(search_query1, search_query2)
            document=policy.get_document(search_query1, search_query2)
            etc=policy.get_etc(search_query1, search_query2)
        else:
            articles_of_association=policy.get_articles_of_association()
            regulation=policy.get_regulation()
            guidelines=policy.get_guidelines()
            rules=policy.get_rules()
            document=policy.get_document()
            etc=policy.get_etc()

        context={
        'articles_of_association': articles_of_association,
        'regulation':regulation,
        'guidelines':guidelines,
        'rules':rules,
        'document':document,
        'etc':etc,
        }

        return render(request, f"compliance/policy/policy.html", context)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)

def get_policy_file():
    pass