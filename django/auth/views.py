from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from auth.src import register, authentication
from django.conf import settings
from py2neo import Graph

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def login_view(request):
    if 1 > graph.evaluate("MATCH (a:Teiren:Account) RETURN COUNT(a)"):
        return redirect('/auth/register/')
    if request.method == 'POST':
        data = dict(request.POST.items())
        username, password = authentication.login_account(data)
        if username == 'fail':
            return render(request, 'auth/login.html', data)
        else:
            user = authenticate(request, username=username, password=password)
            if user is None:
                test = User.objects.create_user(username=username , password=password)
                test.set_password(password)
                test.save()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # User credentials are valid, log the user in
            login(request, user)
            next_url = request.GET.get('next')
            if next_url is not None:
                # Redirect to a success page
                return redirect(next_url)
            else:
                return redirect('/')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('/auth/login/?next=/')

def register_view(request):
    context = {'color': 'teiren', 'message': 'Register To Use Teiren SIEM'}
    if request.method == "POST":
        data = dict(request.POST.items())
        message = register.check_account(data)
        if message == 'check':
            if register.register_account(data) == 'success':
                context = {'color': 'teiren', 'message': 'Register Success! Please Sign In'}
                return render(request, 'auth/register.html', context)
            else:
                message = "Fail To Register. Please Try Again"
        context = {'color': 'danger', 'message': message}
        context.update(data)
    return render(request, 'auth/register.html', context)