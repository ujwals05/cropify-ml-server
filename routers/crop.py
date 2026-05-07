from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ml.crop_pipeline import predict_crop
from services.weather_service import get_weather_by_coords
from fastapi.concurrency import run_in_threadpool

router = APIRouter()


# This defines exactly what JSON the frontend must send
class CropInput(BaseModel):
    lat: float
    lon: float

    nitrogen: float = Field(..., ge=0, le=140,
                            description="Nitrogen content in soil (0-140)")
    phosphorus: float = Field(..., ge=0, le=145,
                              description="Phosphorus content in soil (0-145)")
    potassium: float = Field(..., ge=0, le=205,
                             description="Potassium content in soil (0-205)")
    ph: float = Field(..., ge=0, le=14,
                      description="pH value of soil (0-14)")
    
@router.post("/recommend")
async def recommend_crop(data: CropInput):
    try:
        # 1. Get current weather
        weather = await get_weather_by_coords(data.lat, data.lon)

        # 2. IMPORTANT FIX: get rainfall separately using city fallback logic
        from services.weather_service import _get_5day_rainfall

        # We need city name for forecast API
        city = weather.get("city")

        rainfall_5day = 0.0
        rainfall_month = 0.0

        if city:
            rainfall_5day = await _get_5day_rainfall(city)
            rainfall_month = round((rainfall_5day / 5) * 30, 2)

        # 3. Run ML model
        result = await run_in_threadpool(
            predict_crop,
            nitrogen=data.nitrogen,
            phosphorus=data.phosphorus,
            potassium=data.potassium,
            temperature=weather["temperature"],
            humidity=weather["humidity"],
            ph=data.ph,
            rainfall=rainfall_month
        )

        return {
            "prediction": result,
            "weather": {
                **weather,
                "rainfall_5day": rainfall_5day,
                "rainfall_month_estimate": rainfall_month
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))