from django.shortcuts import render
from django.http import JsonResponse
from common.risk.v1.notification.alert import check_topbar_alert
from common.risk.v1.visual.user.user import user_graph
from common.log.v1.utils import get_log_detail_modal

# Topbar Alert
def topbar_alert(request):
    context = check_topbar_alert()
    return JsonResponse(context)

## Detail Modal
def log_modal(request, modal_type):
    if request.method == 'POST':
        if modal_type == 'help':
            return render(request, "log/help.html")
        elif modal_type == 'details':
            if request.POST['cloud'] == 'Aws':
                context = get_log_detail_modal(dict(request.POST.items()))
            return render(request, "logs/detail_modal.html", context)
        
## Visuals User Details Modal
def user_details(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = dict(request.POST.items())
            context.update(user_graph(context))
        return render(request, 'management/visuals/user/details.html', context)