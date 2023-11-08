from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .src import integration

# Integration
@login_required
def integration_view(request):
    context = integration.list_integration()
    
    return render(request, "M_equipment/integration.html", context)

@login_required
def integration_page(request, equipment):
    if equipment == 'delete':
        if request.method == 'POST':
            data = dict(request.POST.items())
            context = integration.delete_integration(data)
            
            return HttpResponse(context)
        
    return render(request, f"M_equipment/{equipment}.html")

def integration_check_ajax(request, equipment):
    if request.method == 'POST':
        context = integration.integration_check(request)
        
        return JsonResponse(context)

def integration_insert_ajax(request, equipment):
    if request.method == 'POST':
        context = integration.integration_insert(request)
        
        return HttpResponse(context)

def integration_collection_ajax(request, equipment):
    if request.method == 'POST':
        data = dict(request.POST.items())
        context = integration.container_trigger(data, equipment)
        
        return JsonResponse(context)