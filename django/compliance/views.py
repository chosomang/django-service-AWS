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
    if request.method=="POST":
        evidence.add_evidence(dict(request.POST.items()))
        return render(request, f"compliance/evidence_1.html")
    return render(request, f"compliance/evidence_2.html")

# Compliance evidence_3 - 성연
def evidence_view_3(request):
    context={
        'details_list': evidence.get_details()
    }
    return render(request, f"compliance/evidence_3.html", context)