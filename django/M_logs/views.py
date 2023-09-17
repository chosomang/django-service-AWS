from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.log.v1.utils import get_log_page
from common.risk.v1.notification.alert import check_topbar_alert


@login_required
def log_view(request, type):
    context = {'type': type.upper()}
    if type == 'aws':
        context.update(get_log_page(dict(request.GET.items()), type))
    context.update(check_topbar_alert())
    return render(request,f"logs/{type}.html",context)