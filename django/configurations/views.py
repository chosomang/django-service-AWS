from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.src.risk.notification.topbar import check_topbar_alert

HTML_FILE_PATH = 'configurations'

@login_required
def configuration_view(request, config_type):
    return render(request, f"{HTML_FILE_PATH}/{config_type}.html")