import os

from dotenv import load_dotenv
from fastapi import FastAPI
from mangum import Mangum

from src.restaurant_service import get_kakao_api_response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

@app.get("/")
def read_root():
    location_req = {
        "longitude": "127.06283102249932",
        "latitude": "37.514322572335935"
    }

    response = get_kakao_api_response(location_req, 1)
    return response

@app.on_event("startup")
def startup_event():
    import os
    app.state.KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

handler = Mangum(app)
