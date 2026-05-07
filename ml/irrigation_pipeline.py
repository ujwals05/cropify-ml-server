import pickle
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Load all 4 files once at startup
with open(BASE_DIR / "models" / "irrigation_model.pkl", "rb") as f:
    model = pickle.load(f)

with open(BASE_DIR / "models" / "irrigation_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open(BASE_DIR / "models" / "irrigation_target_le.pkl", "rb") as f:
    target_le = pickle.load(f)

with open(BASE_DIR / "models" / "irrigation_le_dict.pkl", "rb") as f:
    le_dict = pickle.load(f)


def get_valid_values() -> dict:
    # Returns valid options for each categorical field
    # Used by frontend to populate dropdowns
    return {
        col: list(le.classes_)
        for col, le in le_dict.items()
    }


def predict_irrigation(
    soil_type: str,
    ph: float,
    moisture: float,
    organic: float,
    ec: float,
    temperature: float,
    humidity: float,
    rainfall: float,
    sunlight: float,
    wind: float,
    crop_type: str,
    crop_growth_stage: str,
    season: str,
    irrigation_type: str,
    water_source: str,
    area: float,
    mulching_used: str,
    previous_irrigation: float,
    region: str
) -> dict:

    # Step 1 — Encode categorical inputs
    # Exact same order as your notebook's user_data list
    user_data = [
        le_dict['Soil_Type'].transform([soil_type])[0],
        ph,
        moisture,
        organic,
        ec,
        temperature,
        humidity,
        rainfall,
        sunlight,
        wind,
        le_dict['Crop_Type'].transform([crop_type])[0],
        le_dict['Crop_Growth_Stage'].transform([crop_growth_stage])[0],
        le_dict['Season'].transform([season])[0],
        le_dict['Irrigation_Type'].transform([irrigation_type])[0],
        le_dict['Water_Source'].transform([water_source])[0],
        area,
        le_dict['Mulching_Used'].transform([mulching_used])[0],
        previous_irrigation,
        le_dict['Region'].transform([region])[0]
    ]

    # Step 2 — Convert to array and scale
    input_array = np.array([user_data])
    input_scaled = scaler.transform(input_array)

    # Step 3 — Predict
    prediction = model.predict(input_scaled)
    probabilities = model.predict_proba(input_scaled)[0]

    # Step 4 — Decode result
    result = target_le.inverse_transform(prediction)[0]
    confidence = round(float(probabilities.max()) * 100, 2)

    return {
        "irrigation_needed": result,
        "confidence": confidence,
        "recommendation": get_recommendation(result)
    }


def get_recommendation(result: str) -> str:
    recommendations = {
        "Yes": "Irrigation is recommended for your field. Based on current soil moisture, weather conditions, and crop growth stage, your crop requires water. Schedule irrigation at early morning or late evening to minimize evaporation loss.",
        "No": "Irrigation is not required at this time. Current soil moisture levels and recent rainfall are sufficient for your crop. Monitor conditions over the next 48 hours before reassessing."
    }
    # Handle cases where result might be 1/0 instead of Yes/No
    if result in recommendations:
        return recommendations[result]
    return f"Irrigation prediction: {result}. Please consult your local agricultural officer for detailed guidance."