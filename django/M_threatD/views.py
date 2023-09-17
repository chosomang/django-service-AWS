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

HTML_FILE_PATH = 'management'

@login_required
def rules_view(request, cloud_type):
    context = {}
    cloud_list = ['aws',
                  'nhn',
                  'ncp',
                  'all',
                  'officekeeper']
    try:
        if cloud_type in cloud_list:
            label_type = cloud_type[0].upper() + cloud_type[1:]
        else:
            # 404 not found
            pass
    finally:
        context.update(get_custom_rules(label_type=label_type))
        context.update(get_default_rules(label_type=label_type))
        context.update(check_topbar_alert())
    
    # comment: 
    #   where is all.html?
    return render(request, f"{HTML_FILE_PATH}/rules/{cloud_type}/{cloud_type}.html", context)

@login_required
def visuals_view(request, cloud_type):
    if cloud_type == 'user':
        context = {'accounts': sorted(get_user_visuals(), key=lambda x: x['total'], reverse=True)}
    elif cloud_type == 'ip':
        map = folium_test('37.5985', '126.97829999999999')
        context = {'map': map}
    else:
        context = {}
    context.update(check_topbar_alert())
    return render(request, f"{HTML_FILE_PATH}/visuals/{cloud_type}.html", context)

@login_required
def alert_view(request, cloud_type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = alert_off(dict(request.POST.items()))
            context.update(neo4j_graph(context))
            context.update(check_topbar_alert())
        return render(request, f"{HTML_FILE_PATH}/alert/{cloud_type}.html", context)
    else:
        if cloud_type == 'details':
            return HttpResponseRedirect('/alert/logs/')
    context = (get_alert_logs())
    context.update(check_topbar_alert())
    return render(request, f"{HTML_FILE_PATH}/alert/{cloud_type}.html", context)