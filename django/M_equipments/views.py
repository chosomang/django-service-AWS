from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .src import integration

# Integration
@login_required
def integration_view(request, pageType):
    if pageType == 'configuration':
        context = integration.list_integration()
        return render(request, f"M_equipment/{pageType}.html", context)
    return render(request, f"M_equipment/{pageType}.html")

@login_required
def registration_page(request, equipment, logType):
    context = {'logType': logType}
    return render(request, f"M_equipment/registration/{equipment}.html", context)

def integration_check_ajax(request, equipment, logType):
    if request.method == 'POST':
        context = integration.integration_check(request, equipment, logType)
        return JsonResponse(context)

def integration_insert_ajax(request, equipment, logType):
    if request.method == 'POST':
        context = integration.integration_insert(request, equipment)
        return HttpResponse(context)

def integration_collection_ajax(request, equipment, logType):
    if request.method == 'POST':
        data = dict(request.POST.items())
        context = integration.container_trigger(data, equipment)
        return JsonResponse(context)

def integration_delete_ajax(request, actionType):
    if request.method == 'POST':
        data = dict(request.POST.items())
        if actionType == 'modal':
            return render(request, 'M_equipment/configuration/delete_modal.html', data)
        context = integration.delete_integration(data)
        return HttpResponse(context)