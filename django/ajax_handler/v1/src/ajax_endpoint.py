from django.shortcuts import render
from django.http import JsonResponse
from common.risk.v1.notification.alert import check_topbar_alert
from common.risk.v1.visual.user.user import user_graph

# Topbar Alert
def topbar_alert(request):
    context = check_topbar_alert()
    return JsonResponse(context)


## Visuals User Details Modal
def user_details(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = dict(request.POST.items())
            context.update(user_graph(context))
        return render(request, 'risk/visuals/user/details.html', context)