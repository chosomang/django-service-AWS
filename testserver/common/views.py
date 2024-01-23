from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .src.topbar import check_topbar_alert

@login_required
# Topbar Alert
def topbar_alert(request):
    print(request.session.get('db_name'))
    context = check_topbar_alert(request.session.get('db_name'))
    return JsonResponse(context)

def error_page(request, exception=None):
    return render(request, '404page.html', status=404)