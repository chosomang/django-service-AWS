from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .src import evidence, lists
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse


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


# Compliance evidence - 성연
def evidence_cate(request):
    '''
    if request.method=="POST":
        add_cate=dict(request.POST.items())
        evidence.add_cate(add_cate)
        return HttpResponseRedirect('/compliance/evidence_cate')
    '''
    context={
        'category_list': evidence.get_category()
    }
    return render(request, f"compliance/evidence_cate.html", context)


# Compliance evidence_cate_add - 성연
def evidence_cate_add(request):
    if request.method=="POST":
        add_cate=dict(request.POST.items())
        return HttpResponse(evidence.add_cate(add_cate))
        
    
    law_list=evidence.get_law_list('com','isms_p')
    context={
        'law_list': law_list,
    }
    return render(request, f"compliance/evidence_cate_add.html",context)

# Compliance evidence_data - 성연
def evidence_data(request, at=None):
    if request.method=="POST":
        title=request.POST['title']

        category=evidence.get_category(title)
        data_list=evidence.get_data(title)
        law_list=evidence.get_law_list('evi',title)
        
        context={
            'title':title,
            'category': category,
            'data_list': data_list,
            'law_list':law_list
        }
        return render(request, f"compliance/evidence_data.html", context)
    else:
        return render(request, f"compliance/evidence_data.html")


# Compliance evidence_4 - 성연쓰 테스트 페이지
def evidence_view_4(request):
    if request.method=="POST":
        context=dict(request.POST.items())
        evidence.add_data(context)
    return render(request, f"compliance/evidence_4.html", context)

# Compliance evidence_data_add - 증적 추가 페이지
def evidence_data_add(request):
    if request.method=="POST":
        title=request.POST['title']
        category=evidence.get_category(title)

        context={
            'category': category,
        }
    return render(request, f"compliance/evidence_data_add.html", context)
