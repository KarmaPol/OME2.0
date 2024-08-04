from typing import Union
from pydantic import BaseModel


class Get_recommendation_request(BaseModel):
    longitude: Union[str, None] = "127.06283102249932"
    latitude: Union[str, None] = "37.514322572335935"
    theme: Union[str, None] = "한식"
    tag: Union[str, None] = None
