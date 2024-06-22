import os
from unittest.mock import patch

from app.dto.get_recommendation_request import Get_recommendation_request
from app.dto.get_recommendation_response import Get_recommendation_response
from app.service.restaurant_service import get_restaurant_recommendation

mock_kakao_result = [
    {
        'place_name': 'Mock Restaurant',
        'category_name': 'Food > Korean',
        'place_url': 'http://mock.restaurant',
        'distance': '100',
        'road_address_name': 'Mock Address'
    }
]

mock_genAI_recommendation = """{'place_name': 'Mock Restaurant', 'category_name': 'Food > Korean', 'place_url': 'http://mock.restaurant', 'distance': '100', 'road_address_name': 'Mock Address'}"""

os.environ['KAKAO_API_KEY'] = 'mock_api_key'

@patch('app.service.restaurant_service.get_kakao_search_result')
@patch('app.service.restaurant_service.get_genAI_recommendation')
def test_get_restaurant_recommendation(mock_get_genAI_recommendation, mock_get_kakao_search_result):
    mock_get_kakao_search_result.return_value = mock_kakao_result
    mock_get_genAI_recommendation.return_value = mock_genAI_recommendation

    get_recommendation_req = Get_recommendation_request(
        longitude="127.06283102249932",
        latitude="37.514322572335935",
        theme="한식",
        tag=None
    )

    response = get_restaurant_recommendation(get_recommendation_req)
    expected_response = Get_recommendation_response(
        title='Mock Restaurant',
        category='Food > Korean',
        link='http://mock.restaurant',
        distance='100',
        address='Mock Address'
    )

    assert response == expected_response
