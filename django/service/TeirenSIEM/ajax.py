from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
import TeirenSIEM.mongo as mongo
import TeirenSIEM.graphdb as graphdb
import TeirenSIEM.rule as rule
import TeirenSIEM.AWS_test as aws
import json


###################################################################

# Topbar Alert
def topbar_alert(request):
    context = aws.alert.check_topbar_alert()
    return JsonResponse(context)

###################################################################

# Log Management
## Help Modal
def log_help(request):
    return render(request, "log/help.html")

## Detail Modal
def log_modal(request, type):
    if request.method == 'POST':
        if type == 'help':
            return render(request, "log/help.html")
        elif type == 'details':
            if request.POST['cloud'] == 'AWS':
                context = aws.log.get_log_detail_modal(dict(request.POST.items()))
            else:
                context = mongo.get_log_detail(dict(request.POST.items()))
            return render(request, "log/detail_modal.html", context)

###################################################################

# Risk Management
## Rule Details Modal
def rule_details(request, type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = {type: aws.rule.default.get_rule_details(dict(request.POST.items()), type)}
        else:
            context = {type: rule.default.get_rule_details(dict(request.POST.items()))}
        return render(request, f"risk/rules/{type}/details.html", context)

#############################################

### Rule Edit
## Rule Edit Modal
def rule_edit_modal(request, type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = aws.rule.edit.get_edit_rule_page(dict(request.POST.items()))
            return render(request, "risk/rules/custom/edit_aws.html", context)
        else:
            context = rule.edit.get_edit_rule_page(dict(request.POST.items()))
            return render(request, "risk/rules/custom/edit.html", context)
## Rule Edit Action
def edit_rule(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = aws.rule.edit.edit_rule(dict(request.POST.items()))
        else:
            context = rule.edit.edit_rule(dict(request.POST.items()))
        return HttpResponse(context)
## Rule Edit Default Rule (Add Action Slot)
def edit_rule_add_action(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = aws.rule.edit.edit_rule_add_action(dict(request.POST.items()))
        else:
            context = rule.edit.edit_rule_add_action(dict(request.POST.items()))
        return render(request, "risk/rules/custom/edit/add_action.html", context)

def edit_add_log_property(request):
    if request.method == 'POST':
        context = dict(request.POST.items())
        context.update({'log_properties': aws.rule.add.get_log_properties(context)})
        return render(request, "risk/rules/custom/edit/property_slot.html", context)

#############################################

### Rule Delete
## Rule Delete Action
def delete_rule(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = aws.rule.delete.delete_rule(dict(request.POST.items()))
        else:
            context = rule.delete.delete_rule(dict(request.POST.items()))
        return HttpResponse(context)

#############################################

### Rule Add
## Rule Add Modal
def rule_add_modal(request, type):
    if request.method == 'POST':
        context = dict(request.POST.items())
        return render(request, 'risk/rules/custom/add.html', context)

## Rule Add Modal Section
def add_rule_section(request, type):
    if request.method == 'POST':
        context = dict(request.POST.items())
        if type == 'property':
            context = dict(request.POST.items())
            context.update({'log_properties': aws.rule.add.get_log_properties(context)})
            return render(request, "risk/rules/custom/add/new_property_slot.html", context)
        else:
            if context:
                if context['cloud'] == 'AWS':
                    if type == 'default':
                        context.update({'actions': aws.rule.add.get_default_actions(context)})
                        return render(request, f'risk/rules/custom/add/{type}.html', context)
                    if type == 'new':
                        context.update({'log_types': aws.rule.add.get_custom_log_types(context)})
                        context.update({'log_properties': aws.rule.add.get_log_properties(context)})
                        return render(request, f'risk/rules/custom/add/{type}_aws.html', context)
                else:
                    if type == 'default':
                        context.update({'actions': rule.add.get_default_actions(context)})
                    if type == 'new':
                        context.update({'log_types': rule.add.get_custom_log_types(context)})
                    return render(request, f'risk/rules/custom/add/{type}.html', context)
            else:
                return render(request, f'risk/rules/custom/add/{type}.html')

## Rule Add Action
def add_rule(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = aws.rule.add.add_rule(dict(request.POST.items()))
        else:
            context = rule.add.add_rule(dict(request.POST.items()))
        return HttpResponse(context)

#############################################

## Rule On_off
def on_off(request, type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = aws.rule.default.rule_on_off(dict(request.POST.items()))
        else:
            context = rule.default.rule_on_off(dict(request.POST.items()))
        return HttpResponse(context)

#############################################
## Visuals User Details Modal
def user_details(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'AWS':
            context = dict(request.POST.items())
            context.update(aws.user.user_graph(context))
        else:
            context = dict(request.POST.items())
            context.update(graphdb.user_graph(context))
        return render(request, 'risk/visuals/user/details.html', context)