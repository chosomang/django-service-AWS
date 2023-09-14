from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import TeirenSIEM.dashboard.dashboard as dashboard
import TeirenSIEM.integration.integrations as integrations
import TeirenSIEM.log.log as log
import TeirenSIEM.risk as risk
import math
import xlwt

# Dashboard
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
    context.update(risk.alert.alert.check_topbar_alert())
    return render(request, "dashboard/dashboard.html", context)

# Log Management
@login_required
def log_view(request, type):
    context = {'type': type.upper()}
    if type == 'aws':
        context.update(log.get_log_page(dict(request.GET.items()), type))
    context.update(risk.alert.alert.check_topbar_alert())
    return render(request,f"log/{type}.html",context)


# Risk Management
## Alert
@login_required
def alert_view(request, type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = risk.alert.alert.alert_off(dict(request.POST.items()))
            context.update(risk.alert.detection.neo4j_graph(context))
            context.update(risk.alert.alert.check_topbar_alert())
        return render(request, f"risk/alert/{type}.html", context)
    else:
        if type == 'details':
            return HttpResponseRedirect('/alert/logs/')
    context = (risk.alert.alert.get_alert_logs())
    context.update(risk.alert.alert.check_topbar_alert())
    return render(request, f"risk/alert/{type}.html", context)

## Rules
@login_required
def rules_view(request, type):
    if type == 'aws':
        context = risk.rule.default.get_custom_rules(type)
        context.update(risk.rule.default.get_default_rules(type))
    context.update(risk.alert.alert.check_topbar_alert())
    return render(request, f"risk/rules/{type}/{type}.html", context)

## Visuals
@login_required
def visuals_view(request, type):
    if type == 'user':
        context = {'accounts': sorted(risk.visual.user.user.get_user_visuals(), key=lambda x: x['total'], reverse=True)}
    elif type == 'ip':
        map = risk.visual.ip.folium.folium_test('37.5985', '126.97829999999999')
        context = {'map': map}
    else:
        context = {}
    context.update(risk.alert.alert.check_topbar_alert())
    return render(request, f"risk/visuals/{type}.html", context)

# Settings
@login_required
def settings_view(request, type):
    context = (risk.alert.alert.check_topbar_alert())
    return render(request, f"settings/{type}.html", context)

# Integration
@login_required
def integration_view(request):
    context = integrations.list_integration()
    context.update(risk.alert.alert.check_topbar_alert())
    return render(request, "integration/integration.html", context)

@login_required
def integration_type(request, type):
    if type == 'delete':
        if request.method == 'POST':
            data = dict(request.POST.items())
            context = integrations.delete_integration(data)
            return HttpResponse(context)
    context=(risk.alert.alert.check_topbar_alert())
    return render(request, f"integration/{type}.html", context)


# Compliance
def compliance_view(request):
    context=(risk.alert.alert.check_topbar_alert())
    return render(request, "compliance/compliance.html", context)

# Report
@login_required
def report_view(request):
    context=(risk.alert.alert.check_topbar_alert())
    return render(request, "compliance/report.html", context)

def report_month_view(request):
    return render(request, "compliance/report.html")