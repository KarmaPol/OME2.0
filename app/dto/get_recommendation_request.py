from typing import Union
from pydantic import BaseModel


class Get_recommendation_request(BaseModel):
    longitude: Union[str, None] # 테스트 편의성을 위해 None
    latitude: Union[str, None]
    theme: Union[str, None]
    tag: Union[str, None]
