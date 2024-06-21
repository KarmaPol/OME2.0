import os

from dotenv import load_dotenv
from fastapi import FastAPI
from mangum import Mangum

from src.restaurant_service import get_kakao_api_response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

@app.get("/", status_code=200)
def health_check():
    return "healthy"

@app.get("/recommend")
def get_recommendation():
    location_req = {
        "longitude": "126.48913062962178",
        "latitude": "33.48631119182245"
    }

    response = get_kakao_api_response(location_req, 1)
    return response

@app.on_event("startup")
def startup_event():
    import os
    app.state.KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
    app.state.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

handler = Mangum(app)
