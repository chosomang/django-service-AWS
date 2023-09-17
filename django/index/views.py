import math
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.src.v1 import dashboard
from common.risk.v1.notification.alert import check_topbar_alert


def index(request):
    return render(request, "index.html")