from django.shortcuts import render
from common.risk.v1.rule.default import get_rule_details
from common.risk.v1.rule.edit import get_edit_rule_page


## Rule Details Modal
def rule_details(request, rule_type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = {
                rule_type: get_rule_details(dict(request.POST.items()), rule_type)
                }
        return render(request, f"management/rules/{rule_type}/details.html", context)
    
def rule_edit_modal(request, rule_type):
    if request.method == 'POST':
        if request.POST['cloud'] == 'Aws':
            context = get_edit_rule_page(dict(request.POST.items()))
            return render(request, "management/rules/custom/edit_aws.html", context)