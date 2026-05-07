from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ml.soil_pipeline import predict_soil_fertility

router = APIRouter()


class SoilInput(BaseModel):
    ndvi: float = Field(
        ..., ge=-1, le=1,
        description="NDVI value (-1 to 1). Healthy vegetation is 0.2 to 0.8"
    )
    moisture: float = Field(
        ..., ge=0, le=1,
        description="Soil moisture (0 to 1). Dry=0.1, Wet=0.4+"
    )
    elevation: float = Field(
        ..., ge=-500, le=9000,
        description="Elevation in meters above sea level"
    )


@router.post("/fertility")
def soil_fertility(data: SoilInput):
    try:
        result = predict_soil_fertility(
            ndvi=data.ndvi,
            moisture=data.moisture,
            elevation=data.elevation
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))