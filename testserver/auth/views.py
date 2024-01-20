# local
from .src.mail import send_mail
from auth.src import authentication
from py2neo import Graph
from .src.register import get_uuid, push_neo4j

# django
from django.conf import settings

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django.shortcuts import render, redirect, HttpResponse

# Excpetion
from django.core.exceptions import ObjectDoesNotExist

# AWS
host = settings.NEO4J['HOST']
port = settings.NEO4J["PORT"]
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']

# Neo4j Connection
graph = Graph(f"bolt://{host}:{port}", auth=(username, password))

def login_(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = get_user_model().objects.get(username=username)
        except ObjectDoesNotExist:
            # 사용자가 없는경우
            messages.warning(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
            return render(request, 'auth/login.html')
            
        user_is_active = user.is_active
        if not user_is_active:
            messages.warning(request, '이메일 인증 후 로그인 해주세요.')
            return render(request, 'auth/login.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            request.session['user_id'] = username
            request.session['uuid'] = get_uuid(username, password)
            if next_url is not None:
                return redirect(next_url)
            else:
                return redirect('/')
        else:
            # 로그인 실패한 경우
            messages.warning(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
            return render(request, 'auth/login.html')
        
    return render(request, 'auth/login.html')

def logout_(request):
    logout(request)
    return redirect('/auth/login/?next=/')

def register_(request):
    context = {'color': 'teiren', 'message': ['Create Your Account', 'TEIREN CLOUD']}
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the user form
            user = form.save(commit=False)
            user.email = request.POST.get('email')
            user.is_active = False
            user.is_staff = False
            user.is_superuser = False
            user.save()
            
            # push to neo4j db
            try:
                push_neo4j(request.POST, _get_client_ip(request))
            except Exception as e:
                print(f'push neo4j error: {e}')
                
            if send_mail(request.POST, user):
                messages.success(request, '회원가입이 완료되었습니다. 메일 인증 후 로그인 해주세요!')
                return render(request, 'auth/register.html', context)
            else:
                messages.warning(request, {'mail': 'fail to send mail'})
        
        else:
            # 폼이 유효하지 않은 경우 에러 메시지를 표시
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f'{field}: {error}')
                
    return render(request, 'auth/register.html', context)

# 이메일 인증 view
def activate_(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        
        # 토큰 검증
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, 'registration/activation_success.html')
        else:
            return render(request, 'registration/activation_failure.html')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request, 'registration/activation_failure.html')

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    