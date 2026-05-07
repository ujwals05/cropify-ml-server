import pickle
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Load model and scaler once at startup
with open(BASE_DIR / "models" / "soil_fertility_model.pkl", "rb") as f:
    model = pickle.load(f)

with open(BASE_DIR / "models" / "soil_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)


def get_fertility_level(value: float) -> str:
    # Exact same logic as your notebook
    if value < 300:
        return "Low"
    elif value < 450:
        return "Medium"
    else:
        return "High"


def predict_soil_fertility(
    ndvi: float,
    moisture: float,
    elevation: float
) -> dict:

    # Step 1 — Arrange input in same order as training
    # Your notebook: X columns are NDVI, Moisture, Elevation
    input_data = np.array([[ndvi, moisture, elevation]])

    # Step 2 — Scale using saved scaler
    input_scaled = scaler.transform(input_data)

    # Step 3 — Predict fertility value
    predicted_value = model.predict(input_scaled)[0]

    # Step 4 — Convert to level using same logic as notebook
    fertility_level = get_fertility_level(predicted_value)

    return {
        "fertility_value": round(float(predicted_value), 2),
        "fertility_level": fertility_level,
        "interpretation": get_interpretation(fertility_level)
    }


def get_interpretation(level: str) -> str:
    # Helpful message for farmer based on level
    interpretations = {
        "Low": "Soil fertility is low. Consider adding organic compost, nitrogen-rich fertilizers, and crop rotation to improve soil health.",
        "Medium": "Soil fertility is moderate. Maintain current practices and consider targeted fertilization based on specific crop needs.",
        "High": "Soil fertility is excellent. Your soil is well-nourished and suitable for most crops without major intervention."
    }
    return interpretations[level]