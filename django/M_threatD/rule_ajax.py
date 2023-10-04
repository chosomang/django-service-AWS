from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from .src.rule import add, default, delete, edit
# Risk Management
## Rule Details Modal
def rule_details(request, ruleType):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = {ruleType: default.get_rule_details(dict(request.POST.items()), ruleType)}
        return render(request, f"M_threatD/rules/{ruleType}/details.html", context)

# #############################################

### Rule Edit
## Rule Edit Modal
def rule_edit_modal(request, cloud):
    if request.method == 'POST':
        context = dict(request.POST.items())
        context.update(edit.get_edit_rule_page(context))
        context.update({'log_properties':add.get_log_properties(context)})
        return render(request, "M_threatD/rules/custom/edit.html", context)

## Rule Edit Action
def edit_rule(request):
    if request.method == 'POST':
        context = edit.edit_rule(dict(request.POST.items()))
        return HttpResponse(context)

# #############################################

### Rule Delete
## Rule Delete Action
def delete_rule(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = delete.delete_rule(dict(request.POST.items()))
        return HttpResponse(context)

# #############################################

### Rule Add
## Rule Add Modal
def rule_add_modal(request, cloud):
    if request.method == 'POST':
        context = dict(request.POST.items())
        return render(request, 'M_threatD/rules/custom/add.html', context)

## Rule Add Modal Section
def add_rule_section(request, section):
    if request.method == 'POST':
        context = dict(request.POST.items())
        context.update({'log_properties': add.get_log_properties(context)})
        if 'flow' in section:
            if section == 'flow_check':
                flow_check = add.get_flow_check(context)
                if isinstance(flow_check, str):
                    return HttpResponse(flow_check)
                context.update(flow_check)
            else:
                context.update(add.get_flow_slot(context))
            return render(request, "M_threatD/rules/custom/add/flow_slot.html", context)
        else:
            if context:
                return render(request, f'M_threatD/rules/custom/add/{section}.html', context)
            else:
                return render(request, f'M_threatD/rules/custom/add/{section}.html')

## Rule Add Action
def add_rule(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = add.add_rule(dict(request.POST.items()))
        return HttpResponse(context)

# #############################################

## Rule On_off
def on_off(request, cloud):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = default.rule_on_off(dict(request.POST.items()))
        return HttpResponse(context)

# #############################################