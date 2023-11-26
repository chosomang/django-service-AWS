from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .src.topbar import check_topbar_alert

@login_required
# Topbar Alert
def topbar_alert(request):
    context = check_topbar_alert()
    return JsonResponse(context)