import math
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from dashboard.src.v1 import dashboard
from common.risk.v1.notification.alert import check_topbar_alert

@login_required
def dashboard_view(request):
    log_total = dashboard.get_log_total()
    threat_total = dashboard.get_threat_total()
    context = {
        "total": format(log_total,","),
        "integration": dashboard.get_integration_total(),
        "threat": format(threat_total,","),
        "threat_ratio": math.ceil(threat_total/log_total*10)/10,
    }
    context.update(dashboard.dashboard_chart())
    context.update(check_topbar_alert())
    return render(request, "dashboard/dashboard.html", context)

