import math
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from common.risk.v1.rule.default import get_default_rules
from common.risk.v1.rule.default import get_custom_rules
from common.risk.v1.visual.ip.folium import folium_test
from common.risk.v1.visual.user.user import get_user_visuals
from common.risk.v1.notification.alert import check_topbar_alert
from common.risk.v1.notification.alert import alert_off
from common.risk.v1.notification.alert import get_alert_logs
from common.risk.v1.notification.detection import neo4j_graph

HTML_FILE_PATH = 'M_threatD'

@login_required
def rules_view(request, cloud):
    context = {}
    cloud_list = ['aws','nhn','ncp','all','officekeeper']
    try:
        if cloud not in cloud_list:
            pass
    finally:
        context = get_custom_rules(cloud)
        context.update(get_default_rules(cloud))
        context.update({'cloud': cloud.capitalize()})
        context.update(check_topbar_alert())
        return render(request, f"risk/rules/rule.html", context)


@login_required
def visuals_view(request, cloud):
    if cloud == 'user':
        context = {'accounts': sorted(get_user_visuals(), key=lambda x: x['total'], reverse=True)}
    elif cloud == 'ip':
        map = folium_test('37.5985', '126.97829999999999')
        context = {'map': map}
    else:
        context = {}
    context.update(check_topbar_alert())
    return render(request, f"{HTML_FILE_PATH}/visuals/{cloud}.html", context)

@login_required
def alert_view(request, cloud):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = alert_off(dict(request.POST.items()))
            context.update(neo4j_graph(context))
            context.update(check_topbar_alert())
        return render(request, f"{HTML_FILE_PATH}/alert/{cloud}.html", context)
    else:
        if cloud == 'details':
            return HttpResponseRedirect('/alert/logs/')
    context = (get_alert_logs())
    context.update(check_topbar_alert())
    return render(request, f"{HTML_FILE_PATH}/alert/{cloud}.html", context)