from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .src import evidence, lists
from django.http import HttpResponseRedirect


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
def evidence_view(request):
    context={
        'category_list': evidence.get_category()
    }
    return render(request, f"compliance/evidence_1.html", context)


# Compliance evidence_2 - 성연
def evidence_view_2(request):
    law_list=evidence.get_law_list()
    chapter_list=evidence.get_chapter_list()
    section_list=evidence.get_section_list()
    article_list=evidence.get_article_list()
    context={
        'law_list': law_list,
        'chapter_list': chapter_list,
        'section_list': section_list,
        'article_list': article_list,
    }

    return render(request, f"compliance/evidence_2.html",context)

# Compliance evidence_3 - 성연
def evidence_view_3(request):
    if request.method=="POST":
        post_data=request.POST['title']

        category=evidence.get_category(post_data)
        data=evidence.get_data(post_data)
        
        context={
            'category': category,
            'data': data,
        }
        return render(request, f"compliance/evidence_3.html", context)
    else:
        return render(request, f"compliance/evidence_3.html")


# Compliance evidence_4 - 성연쓰 테스트 페이지
def evidence_view_4(request, data=None):
    if request.method=="POST":
        data=dict(request.POST.items())
        evidence.add_evidence(data)
    return render(request, f"compliance/evidence_4.html", data)
