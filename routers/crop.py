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
        # Fetch weather from backend
        weather = await get_weather_by_coords(data.lat, data.lon)

        # Run ML model (non-blocking)
        result = await run_in_threadpool(
            predict_crop,
            nitrogen=data.nitrogen,
            phosphorus=data.phosphorus,
            potassium=data.potassium,
            temperature=weather["temperature"],
            humidity=weather["humidity"],
            ph=data.ph,
            rainfall=weather["rainfall"]
        )

        return {
            "prediction": result,
            "weather": weather
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))