from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from .src import log

# Log Management
@login_required
def log_view(request, cloud):
    if request.method == 'POST':
        context = dict(request.POST.items())
        context = (log.get_log_page(context, cloud))
        return render(request,f"M_logs/dataTable.html",context)
    context = dict(request.GET.items())
    context = (log.get_log_page(context, cloud))
    context['cloud']= cloud.capitalize()
    return render(request,f"M_logs/log.html",context)

## Detail Modal
def log_modal(request, cloud):
    if request.method == 'POST':
        if cloud == 'help':
            return render(request, "M_logs/help.html")
        elif cloud == 'details':
            context = log.get_log_detail_modal(dict(request.POST.items()))
            return render(request, "M_logs/detail_modal.html", context)