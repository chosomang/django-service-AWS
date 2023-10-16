from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from .src.notification import notification, detection
from .src.rule import default
from .src.visual.user import user
from .src.visual import ip
from django.http import JsonResponse, HttpResponseRedirect

# Notifications
@login_required
def notification_view(request, threat):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = notification.alert_off(dict(request.POST.items()))
            context.update(detection.neo4j_graph(context))
        return render(request, f"M_threatD/notifications/{threat}.html", context)
    else:
        if threat == 'details':
            return HttpResponseRedirect('/alert/logs/')
    context = (notification.get_alert_logs())
    return render(request, f"M_threatD/notifications/{threat}.html", context)

# Rules
@login_required
def rules_view(request, cloud):
    context = default.get_custom_rules(cloud)
    context.update(default.get_default_rules(cloud))
    context.update({'cloud': cloud.capitalize()})
    return render(request, f"M_threatD/rules/rule.html", context)


## Visuals
@login_required
def visuals_view(request, threat):
    if threat == 'user':
        context = {'accounts': sorted(user.get_user_visuals(), key=lambda x: x['total'], reverse=True)}
    elif threat == 'ip':
        map = ip.folium.folium_test('37.5985', '126.97829999999999')
        context = {'map': map}
    else:
        context = {}
    return render(request, f"M_threatD/visuals/{threat}.html", context)