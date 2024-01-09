from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.http import FileResponse
from .src import evidence, lists, assets, policy
from .models import Document
import json


# Compliance
def compliance_view(request):
    context=' '
    return render(request, f"compliance/compliance.html", context)

# Compliance lists - 현경
@login_required
def compliance_lists_view(request, compliance_type=None):
    if compliance_type:
        context= lists.get_lists_version(compliance_type.capitalize().replace('-','_'))
        context.update({'compliance_type': compliance_type})
        return render(request, f"compliance/compliance_lists/lists.html", context)
    return render(request, f"compliance/compliance_lists.html")

def compliance_lists_modify(request, compliance_type):
    if request.method == "POST":
        data = dict(request.POST.items())
        if "article" in data :
            return HttpResponse(lists.modify_lists_comply(compliance_type.capitalize().replace('-','_'), data))
        data.update({'compliance':lists.get_lists_version(compliance_type.capitalize().replace('-','_'), data)})
        data.update({'compliance_type': compliance_type})
        return render(request, f"compliance/compliance_lists/dataTable.html", data)

@login_required
def compliance_lists_detail_view(request, compliance_type):
    if request.method == 'POST':
        data = dict(request.POST.items())
        data.update(lists.get_lists_details(compliance_type.capitalize().replace('-','_'), data))
        data.update({'compliance_type': compliance_type})
        return render(request, f"compliance/compliance_lists/details.html", data)
    else:
        return redirect(f"/compliance/lists/{compliance_type}")


#Assets Management - 현경
@login_required
def assets_view(request, asset_type=None):
    if request.method == 'POST':
        if asset_type == 'File':
            context = ({'files':assets.get_file_list()})
            return render(request, f"compliance/asset_management/file_view.html", context)
        if asset_type == 'All':
            context = assets.get_asset_list()
        else:
            context = assets.get_asset_list(asset_type)
        return render(request, f"compliance/asset_management/dataTable.html", context)
    else:
        context= assets.get_asset_list()
        return render(request, f"compliance/asset_management.html", context)

@login_required
def assets_table(request, action_type):
    if request.method == 'POST':
        response = assets.asset_table_action(request, action_type)
        return HttpResponse(response)
    else:
        redirect('/auth/login')

@login_required
def assets_action(request, asset_type, action_type):
    if request.method == 'POST':
        if asset_type == 'file':
            return HttpResponse(assets.asset_file_action(request, action_type))
        elif asset_type == 'data':
            return HttpResponse(assets.asset_data_action(request, action_type))
    else:
        redirect('/auth/login')



#########################################################################################
# Data 리스트 출력 페이지
def get_evidence_data(request):
    if request.method == "GET":
        search_query1 = request.GET.get('search_query1', None)
        search_query2 = request.GET.get('search_query2', None)

        if search_query1 and search_query2:
            data_list = evidence.get_data(search_query1, search_query2)
        else:
            data_list = evidence.get_data()
        context = {'data_list': data_list}

        return render(request, "compliance/evidence_management.html", context)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)

def get_compliance(request):
    if request.method == "POST":
        compliance_list = evidence.get_compliance()
        json_data = json.dumps({"compliance_list" :compliance_list})    
        return HttpResponse(json_data, content_type='application/json')

def get_version(request):
    if request.method == "POST":
        compliance_selected=dict(request.POST.items())
        version_list = evidence.get_version(compliance_selected)
        json_data = json.dumps({"version_list" :version_list})    
        return HttpResponse(json_data, content_type='application/json')

def get_article(request):
    if request.method == "POST":
        try:
            version_selected=dict(request.POST.items())
            article_list = evidence.get_article(version_selected)
            json_data = json.dumps({"article_list" :article_list})  
            return HttpResponse(json_data, content_type='application/json')
        except Exception as e:
            # 에러가 발생한 경우
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
# Data 추가
def add_evidence_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.add_data(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
# Data 수정
def mod_evidence_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.mod_data(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    

# Data 삭제
def del_evidence_data(request):
    if request.method=="POST":
        del_data=dict(request.POST.items())

        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.del_data(del_data))   
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)

# file 출력
def get_evidence_file(request):
    if request.method == 'GET':
        # Ajax GET 요청에서 전달된 파라미터 가져오기
        title = request.GET.get('title', None)
        data=evidence.get_data('name', title)
        file_list=evidence.get_file(title)
        compliance_list=evidence.get_compliance_list('evi',title)
        
        context={
            'title':title,
            'data': data,
            'file_list': file_list,
            'compliance_list':compliance_list
        }

        if title:
            return render(request, f"compliance/evidence/file.html", context)
        else:
            # title이 없을 경우 에러 응답
            return JsonResponse({'error': 'Missing title parameter'}, status=400)
    else:
        # GET 이외의 메소드에 대한 처리
        return JsonResponse({'error': 'Invalid method'}, status=400)

# file 추가 시, 함수 동작
def add_evidence_file(request):
    if request.method == 'POST':
        add_file = request.POST.dict()
        uploaded_file = request.FILES.get("add_file")
        file_name = add_file.get('add_name', '')

        # Saving the information in the database
        document = Document(
            title=file_name,
            uploadedFile=uploaded_file
        )
        document.save()

        return HttpResponse(evidence.add_file(add_file))
    else:
        return HttpResponse("Invalid request method")

# file 수정
def mod_evidence_file(request):
    if request.method=="POST":
        mod_file=dict(request.POST.items())

        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.mod_file(mod_file))   
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
        

# file 삭제
def del_evidence_file(request):
    if request.method=="POST":
        del_file=dict(request.POST.items())
        return HttpResponse(evidence.del_file(del_file))
    
def add_com(request):
    if request.method=="POST":
        add_com=dict(request.POST.items())

        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.add_com(add_com))   
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
# Compliance lists_2 - 현경
def integration(request):
    if request.method == 'GET':
        # Ajax GET 요청에서 전달된 파라미터 가져오기
        product_list=evidence.get_product()
        
        context={
            'product_list':product_list
        }

        if product_list:
            return render(request, f"compliance/integration.html", context)
        else:
            # title이 없을 경우 에러 응답
            return JsonResponse({'error': 'Missing title parameter'}, status=400)
    else:
        # GET 이외의 메소드에 대한 처리
        return JsonResponse({'error': 'Invalid method'}, status=400)

# Data 추가
def add_integration(request):
    if request.method=="POST":
        product=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(evidence.add_integration(product))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
  
def get_product(request):
    if request.method=="POST":
        product_list = evidence.get_product()
        json_data = json.dumps({"product_list" :product_list})    
        return HttpResponse(json_data, content_type='application/json')

def get_policy(request):
    if request.method == "GET":
        search_query1 = request.GET.get('search_query1', None)
        search_query2 = request.GET.get('search_query2', None)

        if search_query1 and search_query2:
            policy_data=policy.get_policy(search_query1, search_query2)
        else:
            policy_data=policy.get_policy()

        context={
        'policy':policy_data,
        }

        return render(request, f"compliance/policy/policy.html", context)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)

def get_policy_data(request):
    if request.method == 'GET':
        # Ajax GET 요청에서 전달된 파라미터 가져오기
        policy_name = request.GET.get('policy_name', None)
        data_name = request.GET.get('data_name', None)

        data=policy.get_policy_data(policy_name, data_name)
        file_list=evidence.get_file(data_name)
        
        context={
            'policy':policy_name,
            'data': data,
            'file_list': file_list,
        }

        if policy_name:
            return render(request, f"compliance/policy/file.html", context)
        else:
            # title이 없을 경우 에러 응답
            return JsonResponse({'error': 'Missing title parameter'}, status=400)
    else:
        # GET 이외의 메소드에 대한 처리
        return JsonResponse({'error': 'Invalid method'}, status=400)

def add_policy(request):
    if request.method=="POST":
        policy_name=request.POST.get('policy_name', None)
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(policy.add_policy(policy_name))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
def add_policy_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(policy.add_policy_data(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
def add_policy_file(request):
    if request.method=="POST":
        data=dict(request.POST.items())

        uploaded_file = request.FILES.get("add_file")
        file_name = data.get('add_name', '')

        # Saving the information in the database
        document = Document(
            title=file_name,
            uploadedFile=uploaded_file
        )
        document.save()
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(policy.add_policy_file(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
def del_policy_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(policy.del_policy_data(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
def mod_policy_data(request):
    if request.method=="POST":
        data=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(policy.mod_policy_data(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
def del_policy_file(request):
    if request.method=="POST":
        data=dict(request.POST.items())
   
        try:
            #이걸 JsonResponse로 어케 바꾸지
            return HttpResponse(policy.del_policy_file(data))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=400)