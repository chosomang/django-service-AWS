from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    """Dashboard View using uuid
    각 사용자 별 UUID 를 사용하여서 각 사용자들의 대시보드로 redirect.
    
    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    # user_uuid = request.session.get('uuid')
    # if not user_uuid:
    #     return render(request, "monitoring/info.html")
    # url_with_uuid = reverse('get_metrics_by_uuid', args=[user_uuid])
    # return redirect(url_with_uuid)
    return render(request, "dashboard/dashboard.html")

