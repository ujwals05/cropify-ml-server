from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import crop, weather, soil, irrigation

app = FastAPI(
    title="Cultivai API",
    description="AI-powered crop recommendation system",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models safely
@app.on_event("startup")
async def load_models():
    import joblib
    from routers import crop

    crop.model = joblib.load("ml/models/soil_model.pkl")
    crop.scaler = joblib.load("ml/models/scaler.pkl")
    crop.encoder = joblib.load("ml/models/label_encoder.pkl")

# Routers
app.include_router(crop.router, prefix="/api/crop", tags=["Crop"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(soil.router, prefix="/api/soil", tags=["Soil"])
app.include_router(irrigation.router, prefix="/api/irrigation", tags=["Irrigation"])

# Health check
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "Cultivai backend is running ✅"}