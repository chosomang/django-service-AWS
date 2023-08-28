from django.http import JsonResponse
import TeirenSIEM.mongo as mongo
import math
import datetime
import json
import time
import psutil


def get_log_page(request, type):
    db_handle = mongo.get_db_handle('ts_db')
    collection_handle = mongo.get_collection_handle(db_handle, type.upper())
    
    #페이징
    try:
        if 'page' in request:
            now_page = int(request['page'])  # 페이지
        else:
            raise ValueError
    except ValueError:
        now_page = 1
    except TypeError:
        now_page = 1

    #페이지당 보여줄 로그 개수
    limit = 10
    log_list = collection_handle.find({}).skip((now_page-1)*limit).limit(limit)

    #총 로그 개수
    total_log = collection_handle.count_documents({})
    total_page = math.ceil(total_log / limit)

    page_obj={'log_list': []}
    for log in log_list:
        log['_id'] = str(log['_id'])
        page_obj['log_list'].append(log)

    st_page = max(1, now_page - 5)
    ed_page = min(total_page, now_page + 5)

    if ed_page < 10:
        ed_page=10


    page_obj['has_previous'] = True if now_page > 1 else False
    page_obj['previous_page_number']=now_page-1
    page_obj['paginator'] = {'page_range': range(st_page, ed_page+1)}
    page_obj['now_page']=now_page
    page_obj['has_next'] = True if now_page < total_page else False
    page_obj['next_page_number']=now_page+1
    page_obj['paginator']['num_pages']=total_page
    
    #상품 검색
    product_list=[]
    product_list.append('hello')
    product_list.append('good')
    
    #유저 검색
    user_list=[]
    user_list.append('sungyeon')

    #정규표현식
    regex_list=[]
    regex_list.append('hello')

    response = {
        'page_obj': page_obj,
        'product_list':product_list,
        'user_list':user_list,
        'regex_list':regex_list,
        'total_log': total_log,
        'current_log': [((now_page-1)*10)+1, now_page*10]
    }
    return response