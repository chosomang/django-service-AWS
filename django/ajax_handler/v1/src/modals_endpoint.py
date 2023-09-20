from django.shortcuts import render, HttpResponse
from common.log.v1.utils import get_log_detail_modal
from common.risk.v1.rule.default import get_rule_details, rule_on_off
from common.risk.v1.rule.edit import get_edit_rule_page, edit_rule, edit_rule_add_action
from common.risk.v1.rule.add import get_log_properties, get_default_actions, get_custom_log_types
from common.risk.v1.rule.delete import delete_rule


## Detail Modal
def log_modal(request, modal_type):
    if request.method == 'POST':
        if modal_type == 'help':
            return render(request, "log/help.html")
        elif modal_type == 'details':
            if request.POST['cloud'] == 'Aws':
                context = get_log_detail_modal(dict(request.POST.items()))
            return render(request, "logs/detail_modal.html", context)
        
### Risk Management ###

# Rule Details Modal
def rule_details(request, rule_type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = {rule_type: get_rule_details(dict(request.POST.items()), rule_type)}
        return render(request, f"risk/rules/{rule_type}/details.html", context) # aws not found

### Rule Edit ###

# Edit Modal
def rule_edit_modal(request, cloud_type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = get_edit_rule_page(dict(request.POST.items()))
            return render(request, "risk/rules/custom/edit_aws.html", context)
        
# Edit Action
def edit_rule(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = edit_rule(dict(request.POST.items()))
        return HttpResponse(context)
    
# Edit Default Rule (Add Action Slot)
def edit_rule_add_action(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = edit_rule_add_action(dict(request.POST.items()))
        return render(request, "risk/rules/custom/edit/add_action.html", context)
    
def edit_add_log_property(request):
    if request.method == 'POST':
        context = dict(request.POST.items())
        context.update({'log_properties': get_log_properties(context)})
        return render(request, "risk/rules/custom/edit/property_slot.html", context)
    
### Rule Delete ###

# Delete Action
def delete_rule(request):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = delete_rule(dict(request.POST.items()))
        return HttpResponse(context)
    
### Rule Add ###

# Add Modal
def rule_add_modal(request, cloud_type):
    if request.method == 'POST':
        context = dict(request.POST.items())
        return render(request, 'risk/rules/custom/add.html', context)

# Add Modal Section
def add_rule_section(request, rule_type):
    if request.method == 'POST':
        context = dict(request.POST.items())
        if rule_type == 'property':
            context = dict(request.POST.items())
            context.update({'log_properties': get_log_properties(context)})
            return render(request, "risk/rules/custom/add/property_slot.html", context)
        else:
            if context:
                if context['cloud'] == 'Aws':
                    if rule_type == 'default':
                        context.update({'actions': get_default_actions(context)})
                        return render(request, f'risk/rules/custom/add/{rule_type}.html', context)
                    if rule_type == 'static':
                        context.update({'log_types': get_custom_log_types(context)})
                        context.update({'log_properties': get_log_properties(context)})
                        return render(request, f'risk/rules/custom/add/static.html', context)
            else:
                return render(request, f'risk/rules/custom/add/{rule_type}.html')

### Etc ###

# Rule On_off
def on_off(request, cloud_type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = rule_on_off(dict(request.POST.items()))
        return HttpResponse(context)

### Log Management ###

# Help Modal
def log_help(request):
    return render(request, "log/help.html")


        
