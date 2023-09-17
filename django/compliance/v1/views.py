from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.risk.v1.notification.alert import check_topbar_alert

COMPLIANCE_VERSION = 'v1'

# Compliance
def compliance_view(request):
    context=(check_topbar_alert())
    return render(request, f"compliance/{COMPLIANCE_VERSION}/compliance.html", context)

# Report
def report_view(request):
    context=(check_topbar_alert())
    return render(request, f"compliance/{COMPLIANCE_VERSION}/report.html", context)

def report_month_view(request):
    return render(request, f"compliance/{COMPLIANCE_VERSION}/report.html")