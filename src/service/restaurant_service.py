import json
import os
import re

from dotenv import load_dotenv
from fastapi import HTTPException
import requests

from src.service.genAI_service import generate_content

MAX_RESTAURANT_NUM = 15
load_dotenv()

def get_restaurant_recommendation(location_req, page):
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    kakao_api_key = os.environ['KAKAO_API_KEY']
    headers = {
        'Authorization': 'KakaoAK ' + kakao_api_key
    }
    params = {
        "query": "음식점",
        "category_group_code": "FD6",
        "x": location_req['longitude'],
        "y": location_req['latitude'],
        "radius": 500,
        "size": MAX_RESTAURANT_NUM,
        "page": page,
        "sort": "distance"
    }

    kakao_result = get_kakao_search_result(headers, params, url)
    genAI_recommendation = get_genAI_recommendation(kakao_result, location_req['theme'], location_req['tag'])
    print(genAI_recommendation)
    recommend_data = get_coverted_json(genAI_recommendation)

    return recommend_data

def get_coverted_json(result):
    try:
        if result.startswith('```json'):
            result = re.search(r'```json\n(.*?)\n```', result, re.DOTALL).group(1)
        quote_replaced_json = result.replace("\'", "\"")
        dicted_json = json.loads(quote_replaced_json)
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
    return dicted_json

def get_kakao_search_result(headers, params, url):
    try:
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
