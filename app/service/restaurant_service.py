import itertools
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from fastapi import HTTPException
import requests

from app.dto.get_recommendation_response import Get_recommendation_response
from app.service.genAI_service import generate_content

MAX_RESTAURANT_NUM = 15
load_dotenv()

def get_restaurant_recommendation(get_recommendation_req, page):
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
    pages = [1, 2, 3, 4]
    kakao_results = []

    with ThreadPoolExecutor(len(pages)) as executor:
        futures = {executor.submit(get_kakao_search_result, headers, params, url, page): page for page in pages}

        for future in as_completed(futures):
            try:
                kakao_result = future.result()
                kakao_results.append(kakao_result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    flatten_kakao_results = list(itertools.chain(*kakao_results)) # 이중 리스트 평탄화
    genAI_recommendation = get_genAI_recommendation(flatten_kakao_results, get_recommendation_req.theme, get_recommendation_req.tag)
    recommend_data = get_coverted_json(genAI_recommendation)

    return Get_recommendation_response(
        title=recommend_data['place_name'],
        category=recommend_data['category_name'],
        link=recommend_data['place_url'],
        distance=recommend_data['distance'],
        address=recommend_data['road_address_name']
    )

def get_coverted_json(result):
    try:
        if result.startswith('```json'):
            result = re.search(r'```json\n(.*?)\n```', result, re.DOTALL).group(1)
        quote_replaced_json = result.replace("\'", "\"")
        dicted_json = json.loads(quote_replaced_json)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return dicted_json

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
