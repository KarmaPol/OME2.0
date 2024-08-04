import os
from unittest.mock import patch
import unittest

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

mock_genAI_recommendation = """[{'place_name': 'Mock Restaurant', 'category_name': 'Food > Korean', 'place_url': 'http://mock.restaurant', 'distance': '100', 'road_address_name': 'Mock Address'}]"""

mock_metadata = {'is_end': False, 'pageable_count': 45, 'same_name': {'keyword': '음식점', 'region': [], 'selected_region': ''}, 'total_count': 1}

os.environ['KAKAO_API_KEY'] = 'mock_api_key'

@patch('app.service.restaurant_service.get_kakao_search_result', return_value=mock_kakao_result)
@patch('app.service.restaurant_service.get_genAI_recommendation', return_value=mock_genAI_recommendation)
@patch('app.service.restaurant_service.get_kakao_search_metadata', return_value=mock_metadata)
def test_get_restaurant_recommendation(mock_get_genAI_recommendation,
                                       mock_get_kakao_search_result,
                                       mock_get_kakao_search_metadata):

    get_recommendation_req = Get_recommendation_request(
        longitude="127.06283102249932",
        latitude="37.514322572335935",
        theme="한식",
        tag=None
    )

    return get_restaurant_recommendation(get_recommendation_req)
class TestRestaurantServices(unittest.TestCase):
    def test_get_restaurant_recommendation(self):
        response = test_get_restaurant_recommendation()
        print(response)
        self.assertIsInstance(response, list)
        self.assertIsInstance(response[0], Get_recommendation_response)
        self.assertEqual(response[0].title, 'Mock Restaurant')
