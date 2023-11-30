from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .src import evidence, lists
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse

import json

# Compliance
def compliance_view(request):
    context=''
    return render(request, f"compliance/compliance.html", context)

# Compliance lists - 현경
def lists_view(request):
    context=lists.test() 
    return render(request, f"compliance/lists.html", context)

# Compliance lists_2 - 현경
def lists_view_2(request):
    return render(request, f"compliance/lists_2.html")


# Data 리스트 출력 페이지
def data(request):
    context={
        'data_list': evidence.get_data()
    }
    return render(request, f"compliance/evidence/data.html", context)

def evidence_get_compliance(request):
    if request.method == "POST":
        compliance_list = evidence.get_compliance()
        json_data = json.dumps({"compliance_list" :compliance_list})    
        return HttpResponse(json_data, content_type='application/json')

def get_compliance_articles(request):
    if request.method == "POST":
        compliance_selected=dict(request.POST.items())
        article_list = evidence.get_compliance_articles(compliance_selected)
        json_data = json.dumps({"article_list" :article_list})  
        return HttpResponse(json_data, content_type='application/json')

# Data 추가
def add_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
        return HttpResponse(evidence.add_data(data))
        
    return render(request, f"compliance/evidence/data_add.html")

# Data 삭제
def del_data(request):
    if request.method=="POST":
        del_data=dict(request.POST.items())
        return HttpResponse(evidence.del_data(del_data))

# file 출력 (Data 바로가기)
def file(request, at=None):
    if request.method=="POST":
        title=request.POST['title']

        data=evidence.get_data(title)
        file_list=evidence.get_file(title)
        compliance_list=evidence.get_compliance_list('evi',title)
        
        context={
            'title':title,
            'data': data,
            'file_list': file_list,
            'compliance_list':compliance_list
        }
        return render(request, f"compliance/evidence/file.html", context)
    else:
        return render(request, f"compliance/evidence/file.html")

# file 추가 페이지 view
def add_file(request):
    if request.method=="POST":
        title=request.POST['title']
        data=evidence.get_data(title)

        context={
            'data': data,
        }
    return render(request, f"compliance/evidence/file_add.html", context)

# file 추가 시, 함수 동작
def add_file_func(request):
    if request.method=="POST":
        add_file=dict(request.POST.items())
        return HttpResponse(evidence.add_file(add_file))
        
    return render(request, f"compliance/evidence_cate_add.html")

# file 삭제
def del_file(request):
    if request.method=="POST":
        del_file=dict(request.POST.items())
        return HttpResponse(evidence.del_file(del_file))

