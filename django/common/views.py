from django.http import JsonResponse
from common.src.risk.notification.topbar import check_topbar_alert
# Topbar Alert
def topbar_alert(request):
    context = check_topbar_alert()
    return JsonResponse(context)