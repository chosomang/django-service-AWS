from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

# api index
def index(request):
    return render(request, "api/index.html")

def version(request):
    return render(request, "api/v1.html")