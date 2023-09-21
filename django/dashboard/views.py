import math
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.risk.v1.notification.alert import check_topbar_alert

@login_required
def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")

