from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from common.risk.v1.notification.alert import check_topbar_alert

from M_equipments.src import integration

@login_required
def integration_view(request):
    context = integration.list_integration()
    context.update(check_topbar_alert())
    return render(request, "integration/integration.html", context)

@login_required
def integration_type(request, equipment):
    if equipment == 'delete':
        if request.method == 'POST':
            data = dict(request.POST.items())
            context = integration.delete_integration(data)
            return HttpResponse(context)
    context=(check_topbar_alert())
    return render(request, f"integration/{equipment}.html", context)