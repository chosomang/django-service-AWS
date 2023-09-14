from django.shortcuts import render, HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from TeirenSIEM.models import GridLayout
import TeirenSIEM.gridstack_items as gitems
import json, types

def save_layout(request):
    if len(GridLayout.objects.filter(name=request.POST['name'])) > 0:
        return HttpResponse('이미 저장된 이름입니다. 저장된 대시보드를 삭제하고 다시 시도해 주세요.')
    layout = GridLayout(name=request.POST['name'], data=request.POST['data'])
    layout.save()
    layouts = GridLayout.objects.filter(name=request.POST['name'])
    return HttpResponse(str(len(layouts)))

def load_layout(request):
    layouts = GridLayout.objects.filter(name=request.POST['name'])
    for layout in layouts:
        response = layout.data
    return HttpResponse(response)

def delete_layout(request):
    layouts = GridLayout.objects.filter(name=request.POST['name'])
    for layout in layouts:
        layout.delete()
    return HttpResponse('정상적으로 삭제되었습니다.')

def list_layouts(request):
    if request.method == 'POST':
        names = list(GridLayout.objects.values_list('name', flat=True))
        return JsonResponse(names, safe=False)

def add_item(request, type):
    if request.method == 'POST':
        return getattr(gitems, type)(request)

def list_items(request):
    if request.method == 'POST':
        items = []
        for name, obj in vars(gitems).items():
            if isinstance(obj, types.FunctionType):
                if not any(x in name for x in ['render', '_', 'graph']):
                    items.append(name)
        response = {'items': items}
        return JsonResponse(response)
