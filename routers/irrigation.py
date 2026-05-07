from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ml.irrigation_pipeline import predict_irrigation, get_valid_values

router = APIRouter()


class IrrigationInput(BaseModel):
    soil_type: str = Field(..., description="e.g. Clay, Silt, Sandy")
    ph: float = Field(..., ge=0, le=14, description="Soil pH (0-14)")
    moisture: float = Field(..., ge=0, description="Soil moisture")
    organic: float = Field(..., ge=0, description="Organic Carbon content")
    ec: float = Field(..., ge=0, description="Electrical Conductivity")
    temperature: float = Field(..., ge=0, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    rainfall: float = Field(..., ge=0, description="Rainfall in mm")
    sunlight: float = Field(..., ge=0, le=24, description="Sunlight hours per day")
    wind: float = Field(..., ge=0, description="Wind speed")
    crop_type: str = Field(..., description="e.g. Wheat, Maize, Cotton")
    crop_growth_stage: str = Field(..., description="e.g. Vegetative, Flowering, Harvest")
    season: str = Field(..., description="e.g. Rabi, Zaid, Kharif")
    irrigation_type: str = Field(..., description="e.g. Drip, Canal, Rainfed")
    water_source: str = Field(..., description="e.g. Reservoir, Groundwater")
    area: float = Field(..., ge=0, description="Field area")
    mulching_used: str = Field(..., description="Yes or No")
    previous_irrigation: float = Field(..., ge=0, description="Previous irrigation in mm")
    region: str = Field(..., description="e.g. South, North, Central")


# Main prediction endpoint
@router.post("/predict")
def irrigation_predict(data: IrrigationInput):
    try:
        result = predict_irrigation(
            soil_type=data.soil_type,
            ph=data.ph,
            moisture=data.moisture,
            organic=data.organic,
            ec=data.ec,
            temperature=data.temperature,
            humidity=data.humidity,
            rainfall=data.rainfall,
            sunlight=data.sunlight,
            wind=data.wind,
            crop_type=data.crop_type,
            crop_growth_stage=data.crop_growth_stage,
            season=data.season,
            irrigation_type=data.irrigation_type,
            water_source=data.water_source,
            area=data.area,
            mulching_used=data.mulching_used,
            previous_irrigation=data.previous_irrigation,
            region=data.region
        )
        return result
    except ValueError as e:
        # This catches invalid categorical values
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input value: {str(e)}. Use /api/irrigation/options to see valid values."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper endpoint — returns valid dropdown options for frontend
@router.get("/options")
def irrigation_options():
    return get_valid_values()