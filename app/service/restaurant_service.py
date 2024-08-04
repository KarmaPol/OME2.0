import itertools
import json
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from fastapi import HTTPException
import requests

from app.dto.get_recommendation_response import Get_recommendation_response
from app.service.genAI_service import generate_content

MAX_RESTAURANT_NUM = 15
MAX_INPUT_RESTAURANTS_NUM = 100
THREAD_NUM = 1

load_dotenv()

def get_restaurant_recommendation(get_recommendation_req):
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    kakao_api_key = os.environ['KAKAO_API_KEY']
    headers = {
        'Authorization': 'KakaoAK ' + kakao_api_key
    }
    params = {
        "query": "음식점",
        "category_group_code": "FD6",
        "x": get_recommendation_req.longitude,
        "y": get_recommendation_req.latitude,
        "radius": 500,
        "size": MAX_RESTAURANT_NUM,
        "sort": "distance"
    }

    kakao_results = []

    # 전체 페이지 수 확인 후 호출
    metadata = get_kakao_search_metadata(headers, params, url)
    total_restaurant_num = metadata['total_count']

    page_number = total_restaurant_num // MAX_RESTAURANT_NUM
    pages = [i for i in range(1, page_number+1)]

    with ThreadPoolExecutor(len(pages)) as executor:
        futures = {executor.submit(get_kakao_search_result, headers, params, url, page): page for page in pages}

        for future in as_completed(futures):
            try:
                kakao_result = future.result()
                kakao_results.append(kakao_result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    flatten_kakao_results = list(itertools.chain(*kakao_results))
    unique_kakao_results = []
    seen = set()
    for result in flatten_kakao_results:
        value_tuple = tuple(result.values())
        if value_tuple not in seen:
            seen.add(value_tuple)
            unique_kakao_results.append(result)

    random.shuffle(unique_kakao_results)
    selected_kakao_results = unique_kakao_results[:MAX_INPUT_RESTAURANTS_NUM]

    sublists = []
    sublist_size = len(selected_kakao_results) // THREAD_NUM
    start_index = 0

    for i in range(THREAD_NUM-1):
        end_index = start_index + sublist_size
        sublist = selected_kakao_results[start_index:end_index]
        if len(sublist) != 0:
            sublists.append(sublist)
        start_index = end_index

    sublists.append(selected_kakao_results[start_index:])

    recommendation_responses = []
    with ThreadPoolExecutor(len(sublists)) as executor:
        futures = {executor.submit(get_genAI_recommendation, sublist, get_recommendation_req.theme, get_recommendation_req.tag): sublist for sublist in sublists}

        for future in as_completed(futures):
            try:
                recommend_data = future.result()
                recommend_data = get_coverted_json(recommend_data)
                for data in recommend_data:
                    response = Get_recommendation_response(title=data['place_name'], category=data['category_name'],
                                                           link=data['place_url'], distance=data['distance'],
                                                           address=data['road_address_name'])
                    recommendation_responses.append(response)
            except Exception as e:
                print(e)
                raise HTTPException(status_code=500, detail=str(e))

    return recommendation_responses

def get_coverted_json(result):
    try:
        if result.startswith('```json'):
            result = re.search(r'```json\n(.*?)\n```', result, re.DOTALL).group(1)
        quote_replaced_json = result.replace("\'", "\"")
        dicted_json = json.loads(quote_replaced_json)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return dicted_json

def get_kakao_search_metadata(headers, params, url):
    try:
        params['page'] = 1
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        metadata = response.json()['meta']
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    return metadata

def get_kakao_search_result(headers, params, url, page):
    try:
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        restaurants = response.json()['documents']
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    return restaurants

def get_genAI_recommendation(restaurants, theme, tag):
    try:
        genai_request = {};
        genai_request['restaurants'] = restaurants
        genai_request['theme'] = theme
        genai_request['tag'] = tag

        response = generate_content(genai_request)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return response
