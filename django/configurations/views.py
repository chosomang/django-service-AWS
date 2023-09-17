from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.risk.v1.notification.alert import check_topbar_alert

HTML_FILE_PATH = 'configurations'

@login_required
def configuration_view(request, config_type):
    context = (check_topbar_alert())
    return render(request, f"{HTML_FILE_PATH}/{config_type}.html", context)