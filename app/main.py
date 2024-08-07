import os
from typing import Union

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from mangum import Mangum

from app.dto.get_recommendation_request import Get_recommendation_request
from app.dto.get_recommendation_response import Get_recommendation_response
from app.service.restaurant_service import get_restaurant_recommendation

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

@app.get("/", status_code=200)
def health_check():
    return "healthy"

@app.get("/recommend")
def get_recommendation(
    longitude: Union[str, None] = Query("127.06283102249932"),
    latitude: Union[str, None] = Query("37.514322572335935"),
    theme: Union[str, None] = Query("일식, 한식, 중식, 카페, 아시아음식, 양식, 술집, 샐러드, 브런치"),
) -> list[Get_recommendation_response]:
    request = Get_recommendation_request(
        longitude=longitude,
        latitude=latitude,
        theme=theme,
    )
    response = get_restaurant_recommendation(request)
    return response


@app.on_event("startup")
def startup_event():
    import os
    app.state.KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
    app.state.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
