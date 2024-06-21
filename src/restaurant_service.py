import json
import os
import re

from dotenv import load_dotenv
from fastapi import HTTPException
import requests

from src.genAI_service import generate_content

MAX_RESTAURANT_NUM = 15
load_dotenv()

def get_kakao_api_response(location_req, page):
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
        # "page": page,
        "sort": "distance"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        restaurants = response.json()['documents']
        print(response.json())

        genai_request = {};
        genai_request['restaurants'] = restaurants
        genai_request['theme'] = '한식'

        response = generate_content(genai_request)
        print(response)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    json_string = re.search(r'```json\n(.*?)\n```', response, re.DOTALL).group(1)

    try:
        recommend_data = json.loads(json_string)
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)

    return recommend_data
