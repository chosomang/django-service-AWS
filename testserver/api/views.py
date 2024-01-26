from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.http import JsonResponse
import json
from .models import Metrics
            

API_VERSION = 'v1'
### api view ###
@login_required
def index(request):
    return render(request, "api/index.html")

# API Key Auth
# @csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def health(request):
    return JsonResponse({'status': 'success'})

# AWS Lambda, api-gateway API TESTING #
@csrf_exempt
@require_POST # Only recived Post
def receive_metrics(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            uuid = request.META.get('HTTP_UUID')
            Metrics.objects.create(
                uuid=uuid,
                cpu=data['cpu'],
                memory=data['memory'],
                disk_usage=data['disk_usage'],
                
                read_count=data['disk_io']['read_count'],
                write_count=data['disk_io']['write_count'],
                
                read_bytes=data['disk_io']['read_bytes'],
                write_bytes=data['disk_io']['write_bytes'],
                read_time=data['disk_io']['read_time'],
                write_time=data['disk_io']['write_time'],
                
                read_merged_count=data['disk_io']['read_merged_count'],
                write_merged_count=data['disk_io']['write_merged_count'],
                busy_time=data['disk_io']['busy_time'],
                
                bytes_sent=data['net_io']['bytes_sent'],
                bytes_recv=data['net_io']['bytes_recv'],
                packets_sent=data['net_io']['packets_sent'],
                packets_recv=data['net_io']['packets_recv'],
                
                errin=data['net_io']['errin'],
                errout=data['net_io']['errout'],
                dropin=data['net_io']['dropin'],
                dropout=data['net_io']['dropout'],
                
                instance_id=data['instance-id'],
                instance_type=data['instance-type'],
                public_ipv4=data['public-ipv4'],
                local_ipv4=data['local-ipv4']
            )
            print(f"  Metrics Recived Alerm")
            print(f"  USER:        [{data['UUID']}]")
            print(f"  Instance ID: [{data['instance-id']}]")
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            # JSON 디코딩 오류 처리
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'message': 'Invaild Method'})

def get_metric_data(request, instance_id):
    print(f"instance ID is: {instance_id}")
    try:
        metrics = list(Metrics.objects.filter(instance_id=instance_id).values())
    except Exception as e:
        print(e)
    print(f"metrics data: {metrics}")
    return JsonResponse(metrics, safe=False)

from django.db.models import Max
from django.utils import timezone
import datetime

def get_all_metrics(request, uuid):
    ten_min_ago = timezone.now() - datetime.timedelta(minutes=1)

    # 지난 10분 동안의 사용자 UUID에 해당하는 메트릭 데이터 가져오기
    metrics_data = Metrics.objects.filter(timestamp__gte=ten_min_ago, user_uuid=user_uuid)
    
    latest_metrics = {}
    for metric in metrics_data:
        if metric.instance_id not in latest_metrics:
            latest_metrics[metric.instance_id] = []
        latest_metrics[metric.instance_id].append({
            'instance_id': metric.instance_id,
            'cpu': metric.cpu,
            'memory': metric.memory,
            'disk_usage': metric.disk_usage,
            # 추가 필드...
            'timestamp': metric.timestamp
        })

    # latest_metrics는 이제 각 instance_id에 대한 메트릭 리스트를 포함하는 dict입니다.
    # JsonResponse로 변환하기 위해 리스트로 변경합니다.
    metrics_list = [metrics for metrics in latest_metrics.values()]

    print(f"Metrics Type is: {type(metrics_list)}")
    return JsonResponse(metrics_list, safe=False)

def get_metrics_by_uuid(request, uuid):
    ten_min_ago = timezone.now() - datetime.timedelta(minutes=1)
    print(f"uuid is : {uuid}")

    # 지난 10분 동안의 사용자 UUID에 해당하는 메트릭 데이터 가져오기
    metrics_data = Metrics.objects.filter(timestamp__gte=ten_min_ago, uuid=uuid)
    
    latest_metrics = {}
    for metric in metrics_data:
        if metric.instance_id not in latest_metrics:
            latest_metrics[metric.instance_id] = []
        latest_metrics[metric.instance_id].append({
            'instance_id': metric.instance_id,
            'cpu': metric.cpu,
            'memory': metric.memory,
            'disk_usage': metric.disk_usage,
            'timestamp': metric.timestamp
        })

    # latest_metrics는 이제 각 instance_id에 대한 메트릭 리스트를 포함하는 dict입니다.
    # JsonResponse로 변환하기 위해 리스트로 변경합니다.
    metrics_list = [metrics for metrics in latest_metrics.values()]
    print(metrics_list)
    print(f"Metrics Type is: {type(metrics_list)}")
    return JsonResponse(metrics_list, safe=False)
    
def show_metrics(request):
    latest_metrics = Metrics.objects.last()
    return render(request, 'metrics.html', {'metrics': latest_metrics})

import jwt
@csrf_exempt
def create_jwt_token(request):
    """UUID 를 통하여 사용자에게 jwt token을 발급해주는 api

    Args:
        user_uuid (str): uuid

    Returns:
        str: jwt token
    """
    # user_uuid가 현재 요청을 보낸 사용자의 계정을 인식하고, 데이터 베이스에 저장되어있는 user_uuid랑 일치하는지 검증하는 로직 필요
    
    data = json.loads(request.body.decode('utf-8'))
    user_uuid = data['uuid']
    
    secret_key = "k!ng-g0d-yuwOn#"
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1시간 후 만료
    payload = {
        'user_uuid': user_uuid,
        'exp': expiration_time
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token