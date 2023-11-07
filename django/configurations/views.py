from django.template.loader import render_to_string
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from configurations.src import account

HTML_FILE_PATH = 'configurations'

@login_required
def configuration_view(request, config_type):
    if config_type == 'account':
        context = account.get_account_list()
        return render(request, f"{HTML_FILE_PATH}/{config_type}.html", context)
    return render(request, f"{HTML_FILE_PATH}/{config_type}.html")

@login_required
def account_config(request, config_type):
    if request.method == 'POST':
        data = dict(request.POST.items())
        if config_type == 'verify':
            context = account.verify_account(data)
            if isinstance(context, str):
                return HttpResponse()
            else:
                return render(request, f"{HTML_FILE_PATH}/account/edit.html", context)
        elif config_type == 'edit':
            context = account.edit_account(data)
            return HttpResponse(context)
        elif config_type == 'add':
            context = account.add_account(data)
            return HttpResponse(context)