from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .src import integration
from .src.integration import(integration_check, integration_insert, 
delete_integration, container_trigger, list_integration)

# Integration
@login_required
def integration_view(request, pageType):
    if pageType == 'configuration':
        context = list_integration(request.session.get('db_name'))
        return render(request, f"M_equipment/{pageType}.html", context)
    return render(request, f"M_equipment/{pageType}.html")

def integration_config_ajax(request, actionType):
    if request.method == 'POST':
        data = dict(request.POST.items())
        if actionType == 'modal':
            return render(request, 'M_equipment/configuration/modal.html', data)
        if actionType == 'check':
            return 
        if actionType == 'delete':
            context = delete_integration(request=request)
            return JsonResponse(context)
        if actionType == 'trigger':
            context = container_trigger(request=request)
            return JsonResponse(context)

@login_required
def registration_page(request, equipment, logType):
    context = {'logType': logType}
    return render(request, f"M_equipment/registration/{equipment}.html", context)

def integration_registration_ajax(request, equipment, logType, actionType):
    if request.method == 'POST':
        if actionType == 'check':
            context = integration_check(request, equipment, logType)
            return JsonResponse(context)
        elif actionType == 'insert':
            context = integration_insert(request, equipment)
            return HttpResponse(context)