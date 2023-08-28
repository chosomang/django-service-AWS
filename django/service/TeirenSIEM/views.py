from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .folium_test import folium_test
import TeirenSIEM.dashboard as dash
import TeirenSIEM.graphdb as graphdb
import TeirenSIEM.rule as rule
import TeirenSIEM.integrations as integrations
import TeirenSIEM.log as log
import TeirenSIEM.AWS_test as aws
import math
import xlwt

# Dashboard
@login_required
def dashboard(request):
    #log = dash.get_log_total()
    log_total = aws.dashboard.get_log_total()
    #threat_total = dash.get_threat_total()
    threat_total = aws.dashboard.get_threat_total()
    context = {
        "total": format(log_total,","),
        "integration": dash.get_integration_total(),
        "threat": format(threat_total,","),
        "threat_ratio": math.ceil(threat_total/log_total*10)/10,
    }
    context.update(dash.dashboard_chart())
    context.update(aws.alert.check_topbar_alert())
    return render(request, "dashboard.html", context)

# Log Management
@login_required
def log_view(request, type):
    context = {'type': type.upper()}
    if type == 'aws':
        context.update(aws.log.get_log_page(dict(request.GET.items()), type))
    else:
        context.update(log.get_log_page(dict(request.GET.items()), type))
    context.update(aws.alert.check_topbar_alert())
    return render(request,f"log/{type}.html",context)


# Risk Management
## Alert
@login_required
def alert(request, type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = aws.alert.alert_off(dict(request.POST.items()))
            context.update(aws.alert.neo4j_graph(context))
            context.update(aws.alert.check_topbar_alert())
        else:
            context = aws.alert.alert_off(dict(request.POST.items()))
            context.update(aws.alert.neo4j_graph(context))
            context.update(aws.alert.check_topbar_alert())
        return render(request, f"risk/alert/{type}.html", context)
    else:
        if type == 'details':
            return HttpResponseRedirect('/alert/logs/')
    context = (aws.alert.get_alert_logs())
    context.update(aws.alert.check_topbar_alert())
    return render(request, f"risk/alert/{type}.html", context)

## Rules
@login_required
def rules(request, type):
    if type == 'all':
        context = rule.default.get_all_rules()
        context['rules'] += aws.rule.default.get_all_rules()['rules']
        context.update(aws.alert.check_topbar_alert())
        return render(request, f"risk/rules/{type}.html", context)
    if type == 'aws':
        context = aws.rule.default.get_custom_rules(type)
        context.update(aws.rule.default.get_default_rules(type))
    else:
        context = rule.default.get_custom_rules(type)
        context.update(rule.default.get_default_rules(type))
    context.update(aws.alert.check_topbar_alert())
    return render(request, f"risk/rules/{type}/{type}.html", context)

## Visuals
@login_required
def visuals(request, type):
    if type == 'user':
        context = {'accounts': sorted(graphdb.get_user_visuals()+aws.user.get_user_visuals(), key=lambda x: x['total'], reverse=True)}
    elif type == 'ip':
        map = folium_test('37.5985', '126.97829999999999')
        context = {'map': map}
    else:
        context = {}
    context.update(aws.alert.check_topbar_alert())
    return render(request, f"risk/visuals/{type}.html", context)

# Settings
@login_required
def settings(request, type):
    context = (aws.alert.check_topbar_alert())
    return render(request, f"settings/{type}.html", context)

# Integration
@login_required
def integration(request):
    context = integrations.list_integration()
    context.update(aws.alert.check_topbar_alert())
    return render(request, "integration/integration.html", context)

@login_required
def integration_type(request, type):
    if type == 'delete':
        if request.method == 'POST':
            data = dict(request.POST.items())
            context = integrations.delete_integration(data)
            return HttpResponse(context)
    context=(aws.alert.check_topbar_alert())
    return render(request, f"integration/{type}.html", context)


# Compliance
def compliance(request):
    context=(aws.alert.check_topbar_alert())
    return render(request, "compliance/compliance.html", context)

# Report
@login_required
def report(request):
    context=(aws.alert.check_topbar_alert())
    return render(request, "compliance/report.html", context)

def report_month(request):
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment;filename*=UTF-8\'\'[Teiren]Month Report.xls'
    wb = xlwt.Workbook(encoding='ansi')  # encoding은 ansi로 해준다.
    ws = wb.add_sheet('출입 신청')  # 시트 추가

    row_num = 0
    col_names = ['날짜', '업체명', '직책', '이름']

    wb.save(response)

    return response