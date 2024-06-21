import os

from dotenv import load_dotenv
from fastapi import FastAPI
from mangum import Mangum

from src.service.restaurant_service import get_restaurant_recommendation

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

@app.get("/", status_code=200)
def health_check():
    return "healthy"

@app.get("/recommend")
def get_recommendation(longitude: str="127.06283102249932", latitude: str="37.514322572335935", theme: str="한식", tag: str=""):
    location_req = {
        "longitude": longitude,
        "latitude": latitude,
        "theme": theme,
        "tag": tag
    }

    response = get_restaurant_recommendation(location_req, 1)
    return response

@app.on_event("startup")
def startup_event():
    import os
    app.state.KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
    app.state.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

handler = Mangum(app)
