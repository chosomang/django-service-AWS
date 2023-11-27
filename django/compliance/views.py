from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from common.risk.v1.notification.alert import check_topbar_alert
from .src import evidence, lists, lists_2, version_modify
from . import models


# Compliance
def compliance_view(request):
    context=''
    return render(request, f"compliance/compliance.html", context)

# Compliance lists - 현경
def lists_view(request):

    context= lists.version()
    return render(request, f"compliance/lists.html", context)

# Compliance lists_2 - 현경
def lists_view_2(request):
    if request.method == "POST":
        data = dict(request.POST.items())
        result = lists_2.test(data)
        data.update(result)
        return render(request, f"compliance/lists_2.html", data)

def versionModify(request):
    if request.method == "POST":
        data = dict(request.POST.items())
        data.update({'compliance':version_modify.version(data)})
        return render(request, f"compliance/version_list.html", data)

# Compliance evidence - 성연
def evidence_view(request):
    context=evidence.test()
    return render(request, f"compliance/evidence.html", context)


# Compliance evidence_2 - 성연
def evidence_view_2(request):
    context=''
    return render(request, f"compliance/evidence_2.html", context)

# def addSection(request, sectionType):
#     context = dict(request.POST.items())
#     if context['version'] == '1':
#         context = addSection.addSection(data)
#     return render(request, f"compliance/section/{sectionType}.html", context)

