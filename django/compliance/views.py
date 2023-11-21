from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.risk.v1.notification.alert import check_topbar_alert
from .src import evidence, lists


# Compliance
def compliance_view(request):
    context=''
    return render(request, f"compliance/compliance.html", context)

# Compliance lists - 현경
def lists_view(request):
    '''
        src/lists.py에 있는 값 가져와서 html한테 넘겨주는 코드
        lists.test()는 상단에서 import 해줬음
    '''
    context=lists.test() 
    return render(request, f"compliance/lists.html", context)

# Compliance lists_2 - 현경
def lists_view_2(request):
    return render(request, f"compliance/lists_2.html")


# Compliance evidence - 성연
def evidence_view(request):
    context=evidence.test()
    return render(request, f"compliance/evidence.html", context)


# Compliance evidence_2 - 성연
def evidence_view_2(request):
    context=''
    return render(request, f"compliance/evidence_2.html", context)