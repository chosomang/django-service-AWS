from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .src import evidence, lists
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.http import Http404
import json

# Compliance lists - 현경
def lists_view(request):
    context=lists.test() 
    return render(request, f"compliance/lists.html", context)

# Compliance lists_2 - 현경
def lists_view_2(request):
    return render(request, f"compliance/lists_2.html")



@login_required
def evidence_view(request):
    context= {'category_list': evidence.get_category_list()}
    return render(request, f"compliance/evidence.html", context)

@login_required
def evidence_action(request, actionType):
    if request.method=="POST":
        data=dict(request.POST.items())
        if actionType == 'delete':
            context = evidence.del_cate(data)
        elif actionType == 'add':
            context = evidence.add_cate(data)
        return HttpResponse(context)

@login_required
def evidence_data(request, dataName):
    if request.method=="POST":
        context = {'title':dataName}
        context.update(evidence.get_evidence_data(dataName))
        return render(request, f"compliance/evidence/evidence_data.html", context)
    else:
        raise Http404('test')

def evidence_get_compliance(request):
    if request.method == "POST":
        compliance_list = evidence.get_compliance()
        json_data = json.dumps({"compliance_list" :compliance_list})    
        return HttpResponse(json_data, content_type='application/json')

def evidence_get_compliance_articles(request):
    if request.method == "POST":
        compliance_selected=dict(request.POST.items())
        article_list = evidence.get_compliance_articles(compliance_selected)
        json_data = json.dumps({"article_list" :article_list})  
        return HttpResponse(json_data, content_type='application/json')

def evidence_get_laws(request):
    if request.method == "POST":
        law_list = evidence.get_laws()
        json_data = json.dumps({"law_list" :law_list})
        return HttpResponse(json_data, content_type='application/json')

def evidence_get_laws_chapter(request):
    if request.method == "POST":
        law_seleted=dict(request.POST.items())
        chapter_list = evidence.get_law_chapters(law_seleted)
        json_data = json.dumps({"chapter_list" :chapter_list})  
        return HttpResponse(json_data, content_type='application/json')







# Compliance evidence_data_add - 증적 추가 페이지
def evidence_data_add(request):
    if request.method=="POST":
        title=request.POST['title']
        category=evidence.get_category(title)

        context={
            'category': category,
        }
    return render(request, f"compliance/evidence_data_add.html", context)

# Compliance evidence_data_add - 증적 추가 페이지
def evidence_data_add_result(request):
    if request.method=="POST":
        add_data=dict(request.POST.items())
        return HttpResponse(evidence.add_data(add_data))
        
    return render(request, f"compliance/evidence_cate_add.html")

def evidence_data_del(request):
    if request.method=="POST":
        del_data=dict(request.POST.items())
        return HttpResponse(evidence.del_data(del_data))

