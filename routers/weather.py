from fastapi import APIRouter
from pydantic import BaseModel
from services.weather_service import get_weather_by_city, get_weather_by_coords

router = APIRouter()


# GET weather by city
@router.get("/city/{city_name}")
async def weather_by_city(city_name: str):
    return await get_weather_by_city(city_name)


# Input model
class CoordsInput(BaseModel):
    lat: float
    lon: float


# POST weather by coordinates
@router.post("/coords")
async def weather_by_coords(data: CoordsInput):
    return await get_weather_by_coords(data.lat, data.lon)