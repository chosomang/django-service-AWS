from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.log.v1.utils import get_log_page
from common.risk.v1.notification.alert import check_topbar_alert


@login_required
def log_view(request, cloud):
    if request.method == 'POST':
        context = dict(request.POST.items())
        context = (get_log_page(context, cloud))
        return render(request,f"log/dataTable.html",context)
    context = dict(request.GET.items())
    context = (get_log_page(context, cloud))
    context['cloud']= cloud.capitalize()
    context.update(check_topbar_alert())
    return render(request,f"log/log.html",context)