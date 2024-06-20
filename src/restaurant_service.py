import os

from dotenv import load_dotenv
from fastapi import HTTPException
import requests

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
        "page": page,
        "sort": "distance"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return response.json()
